"""Real PostgreSQL regression; TEST_DATABASE_URL must target an isolated test DB.
Each case owns a random schema and removes only that schema during cleanup.
Optional TEST_SCHEMA_SQL exercises an exported legacy schema instead of ORM DDL.
"""
import asyncio
import json
import os
from pathlib import Path
import secrets
import sys
import unittest
import uuid

ROOT = Path(os.environ.get('BOARD_PROJECT_ROOT', str(Path(__file__).resolve().parents[1])))
sys.path.insert(0, str(ROOT / 'src'))
# This process uses an ephemeral signing key, never the application's real key.
os.environ['JWT_SECRET_KEY'] = secrets.token_hex(64)
from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.engine import make_url
from main import app
from shared.core import database
from shared.core.models import Base
from shared.core.exceptions import ForbiddenException
from user.infrastructure.models import UserModel
from user.infrastructure.security import BcryptPasswordHasher
from user.presentation.dependencies import provide_user_service
from board.infrastructure.sqlalchemy.models import BoardModel, PostModel, CommentModel
from auth.infrastructure.models import TokenBlacklistModel

TEST_URL = os.environ.get('TEST_DATABASE_URL')

@unittest.skipUnless(TEST_URL, 'Set TEST_DATABASE_URL to an isolated PostgreSQL test database')
class PostgreSQLTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        url=make_url(TEST_URL)
        if not url.database or not any(word in url.database.lower() for word in ['test','verification']):
            raise RuntimeError('Refusing a database whose name does not identify it as a test database')
        self.schema='board_test_'+uuid.uuid4().hex
        self.engine=create_async_engine(TEST_URL,connect_args={'server_settings':{'search_path':self.schema}})
        self.original_factory=database.AsyncSessionLocal
        self.overrides=app.dependency_overrides.copy()
        self.factory=async_sessionmaker(self.engine,expire_on_commit=False)
        database.AsyncSessionLocal=self.factory
        self.addAsyncCleanup(self.cleanup_schema)
        async with self.engine.begin() as conn:
            await conn.execute(text('CREATE SCHEMA '+self.schema))
            if os.environ.get('TEST_SCHEMA_SQL'):
                ddl=Path(os.environ['TEST_SCHEMA_SQL']).read_text().replace('public.',self.schema+'.')
                ddl='\n'.join(line for line in ddl.splitlines() if not line.startswith('\\'))
                raw=await conn.get_raw_connection()
                await raw.driver_connection.execute(ddl)
                await conn.execute(text('SET search_path TO '+self.schema))
            else:await conn.run_sync(Base.metadata.create_all)
        self.password='Regression1!'
        async with self.factory() as session:
            session.add(UserModel(id=uuid.uuid4(),email='admin@example.com',name='Admin',password_hash=BcryptPasswordHasher().hash(self.password),role='ADMIN',resign=False))
            session.add_all([BoardModel(board_id='qna',board_name='QnA'),BoardModel(board_id='freetalk',board_name='Free Talk',page_size=5)])
            await session.commit()
        self.admin=await self.login('admin@example.com')

    async def cleanup_schema(self):
        database.AsyncSessionLocal=self.original_factory
        app.dependency_overrides.clear();app.dependency_overrides.update(self.overrides)
        async with self.engine.begin() as conn:await conn.execute(text('DROP SCHEMA IF EXISTS '+self.schema+' CASCADE'))
        await self.engine.dispose()

    async def call(self,method,path,body=None,token=None,expected=200):
        from urllib.parse import urlsplit
        url=urlsplit(path);sent=[]
        headers=[(b'content-type',b'application/json')]
        if token is not None:headers.append((b'authorization',('Bearer '+token).encode()))
        scope={'type':'http','asgi':{'version':'3.0','spec_version':'2.4'},'http_version':'1.1','method':method,'scheme':'http','path':url.path,'raw_path':url.path.encode(),'query_string':url.query.encode(),'root_path':'','headers':headers,'client':('test',1),'server':('test',80)}
        async def receive():return {'type':'http.request','body':json.dumps(body).encode() if body is not None else b'','more_body':False}
        async def send(message):sent.append(message)
        try:await asyncio.wait_for(app(scope,receive,send),10)
        except Exception:
            if expected!=500:raise
        codes=[message['status'] for message in sent if message['type']=='http.response.start']
        self.assertEqual(codes,[expected],'Unexpected HTTP status; credentials omitted')
        raw=b''.join(message.get('body',b'') for message in sent if message['type']=='http.response.body')
        self.assertNotIn(self.password.encode(),raw,'Password must not appear in response')
        if not raw:return None
        try:return json.loads(raw)
        except json.JSONDecodeError:return raw.decode()

    async def login(self,email,password=None):
        result=await self.call('POST','/v1/auth/login',{'email':email,'password':password or self.password})
        return result['access_token']

    async def member(self,email='member@example.com'):
        result=await self.call('POST','/v1/users',{'email':email,'name':'Member','password':self.password},expected=201)
        return result['data']['id'],await self.login(email)

    async def test_signup_password_logout_and_identity(self):
        uid,token=await self.member()
        identity=await self.call('GET','/ui/session',token=token);self.assertEqual(identity['role'],'USER');self.assertEqual(identity['user_id'],uid)
        await self.call('PATCH',f'/v1/users/{uid}/password',{'old_password':self.password,'new_password':'Changed123!'},token=token)
        await self.call('POST','/v1/auth/login',{'email':'member@example.com','password':self.password},expected=401)
        new=await self.login('member@example.com','Changed123!')
        await self.call('POST','/v1/auth/logout',token=new,expected=204)
        await self.call('GET','/ui/session',token=new,expected=401)
        await self.call('GET','/ui/session',token='invalid',expected=401)

    async def test_board_duplicates_soft_delete_and_preservation(self):
        for bid in ['QNA','freetalk']:
            await self.call('POST','/v1/boards',{'board_id':bid,'board_name':'Overwrite'},token=self.admin,expected=409)
        board=await self.call('GET','/v1/boards/qna');self.assertEqual(board['board_name'],'QnA')
        await self.call('POST','/v1/boards',{'board_id':'newboard','board_name':'New'},token=self.admin,expected=201)
        await self.call('PUT','/v1/boards/newboard',{'board_name':'Changed','page_size':5},token=self.admin)
        await self.call('DELETE','/v1/boards/newboard',token=self.admin,expected=204)
        await self.call('POST','/v1/boards',{'board_id':'newboard','board_name':'Restore'},token=self.admin,expected=409)
        await self.call('GET','/v1/boards/newboard',expected=404)

    async def test_concurrent_board_insert_is_not_upsert(self):
        # Explicit status collection without swallowing arbitrary failures.
        async def run(name):
            try:await self.call('POST','/v1/boards',{'board_id':'raceboard','board_name':name},token=self.admin,expected=201);return name,201
            except AssertionError as error:
                self.assertIn('[409]',str(error));return name,409
        results=await asyncio.gather(run('First'),run('Second'))
        self.assertEqual(sorted(code for _,code in results),[201,409])
        winner=next(name for name,code in results if code==201)
        board=await self.call('GET','/v1/boards/raceboard');self.assertEqual(board['board_name'],winner)

    async def test_member_guest_admin_post_comment_crud(self):
        _,member=await self.member();_,other=await self.member('other@example.com')
        for guest in [False,True]:
            fields={'guest_name':'Guest','guest_password':'Guest123!'} if guest else {}
            token=None if guest else member
            post=await self.call('POST','/v1/boards/qna/posts',{'title':'Post','content':'Body',**fields},token,201);pid=post['post_id']
            comment=await self.call('POST',f'/v1/posts/{pid}/comments',{'content':'Comment',**fields},token,201);cid=comment['comment_id']
            await self.call('GET',f'/v1/posts/{pid}',token=token)
            await self.call('GET',f'/v1/posts/{pid}/comments',token=token)
            await self.call('PUT',f'/v1/posts/{pid}',{'title':'Denied','content':'Denied'},other,403)
            await self.call('DELETE',f'/v1/comments/{cid}',token=other,expected=403)
            password={'guest_password':'Guest123!'} if guest else {}
            await self.call('PUT',f'/v1/posts/{pid}',{'title':'Updated','content':'Updated',**password},token)
            await self.call('PUT',f'/v1/comments/{cid}',{'content':'Updated',**password},token)
            await self.call('PUT',f'/v1/posts/{pid}',{'title':'Admin','content':'Admin'},self.admin)
            await self.call('PUT',f'/v1/comments/{cid}',{'content':'Admin'},self.admin)
            await self.call('DELETE',f'/v1/comments/{cid}',token=self.admin,expected=204)
            await self.call('DELETE',f'/v1/posts/{pid}',token=self.admin,expected=204)

    async def test_permission_levels(self):
        _,member=await self.member()
        keys=['edit_role','view_role','list_role','comment_list_role','comment_edit_role']
        for role in ['ALL','USER','ADMIN']:
            bid='role'+role.lower()
            await self.call('POST','/v1/boards',{'board_id':bid,'board_name':'Role','authority':dict.fromkeys(keys,role)},self.admin,201)
            for token,allowed in [(None,role=='ALL'),(member,role!='ADMIN'),(self.admin,True)]:
                await self.call('GET',f'/v1/boards/{bid}/posts',token=token,expected=200 if allowed else 403)
            post=await self.call('POST',f'/v1/boards/{bid}/posts',{'title':'Admin','content':'Admin'},self.admin,201)
            await self.call('POST',f"/v1/posts/{post['post_id']}/comments",{'content':'Admin'},self.admin,201)
        await self.call('POST','/v1/boards',{'board_id':'denied','board_name':'Denied'},member,403)

    async def test_pagination_and_all_six_search_types(self):
        async with self.factory() as session:
            admin=await session.scalar(select(UserModel).where(UserModel.email=='admin@example.com'))
            session.add_all([PostModel(board_id='freetalk',title='Needle '+str(i),content='Needle',author_id=admin.id,author_name='Admin') for i in range(21)])
            await session.commit()
        for query,size,pages in [('',5,5),('?page_size=10',10,3)]:
            result=await self.call('GET','/v1/boards/freetalk/posts'+query)
            self.assertEqual((result['total_count'],result['page_size'],result['total_pages'],len(result['items'])),(21,size,pages,size))
        for kind,keyword in [('ALL','Needle'),('TITLE','Needle'),('CONTENT','Needle'),('TITLE_CONTENT','Needle'),('AUTHOR_NAME','Admin'),('AUTHOR_EMAIL','admin@example.com')]:
            result=await self.call('GET',f'/v1/boards/freetalk/posts?search_type={kind}&keyword={keyword}')
            self.assertEqual(result['total_count'],21)
        result=await self.call('GET','/v1/boards/qna/posts');self.assertEqual(result['total_pages'],0)

    async def test_bcrypt_boundaries(self):
        for password,code in [('a'*69+'1!x',201),('a'*70+'1!x',400)]:
            await self.call('POST','/v1/users',{'email':f'size{code}@example.com','name':'Member','password':password},expected=code)
        for password,code in [('가'*24,201),('가'*25,400)]:
            await self.call('POST','/v1/boards/qna/posts',{'title':'Guest','content':'Body','guest_name':'Guest','guest_password':password},expected=code)
        await self.call('POST','/v1/auth/login',{'email':'admin@example.com','password':'a'*73},expected=401)

    async def test_commit_failure_rollback(self):
        post=await self.call('POST','/v1/boards/qna/posts',{'title':'Seed','content':'Seed'},self.admin,201)
        class FailingCommit(AsyncSession):
            async def commit(self):raise RuntimeError('Injected test-only commit failure')
        cases=[('/v1/users',{'email':'failed@example.com','name':'Failed','password':self.password},None,UserModel),
               ('/v1/boards',{'board_id':'commitfailed','board_name':'Failed'},self.admin,BoardModel),
               ('/v1/boards/qna/posts',{'title':'Failed','content':'Failed'},self.admin,PostModel),
               (f"/v1/posts/{post['post_id']}/comments",{'content':'Failed'},self.admin,CommentModel)]
        for path,body,token,model in cases:
            async with self.factory() as session:before=await session.scalar(select(func.count()).select_from(model))
            database.AsyncSessionLocal=async_sessionmaker(self.engine,class_=FailingCommit,expire_on_commit=False)
            try:await self.call('POST',path,body,token,500)
            finally:database.AsyncSessionLocal=self.factory
            async with self.factory() as session:self.assertEqual(await session.scalar(select(func.count()).select_from(model)),before)

    async def test_service_exception_rollback(self):
        from wiring.user import create_user_service
        class FailingService:
            async def register_user(self,**kwargs):
                await self.inner.register_user(**kwargs)
                raise ForbiddenException('Injected service failure')
        from fastapi import Depends
        def failed(inner=Depends(create_user_service)):
            instance=FailingService();instance.inner=inner;return instance
        app.dependency_overrides[provide_user_service]=failed
        await self.call('POST','/v1/users',{'email':'servicefailed@example.com','name':'Failed','password':self.password},expected=403)
        async with self.factory() as session:self.assertIsNone(await session.scalar(select(UserModel).where(UserModel.email=='servicefailed@example.com')))

    async def test_templates_openapi_and_health(self):
        for path in ['/boards','/boards/qna','/boards/qna/write','/posts/1','/posts/1/edit','/signup','/account','/manage/boards']:
            result=await self.call('GET',path);self.assertIn('<!doctype html>',result)
        await self.call('GET','/health')
        schema=await self.call('GET','/openapi.json');self.assertIn('/v1/boards',schema['paths']);self.assertNotIn('/ui/session',schema['paths'])

if __name__=='__main__':unittest.main()
