(() => {
    'use strict';
    const UI = window.BoardUI;
    const { $, token, request, status, showError, element } = UI;
    const json = (method, data) => ({ method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    const bytes = value => new TextEncoder().encode(value).length;
    function checkPassword(value) { if (bytes(value) > 72) throw new Error('비밀번호는 UTF-8 기준 72바이트 이하여야 합니다.'); }
    function guestFields() {
        document.querySelectorAll('[data-guest-create]').forEach(fieldset => {
            fieldset.hidden = !!token();
            fieldset.querySelectorAll('input').forEach(input => { input.disabled = !!token(); });
        });
    }
    function guestData(form) {
        if (token()) return {};
        const guest_password = form.elements.guest_password.value;
        checkPassword(guest_password);
        return {guest_name: form.elements.guest_name.value, guest_password};
    }
    function bind(form, output, callback) {
        if (!form) return;
        form.addEventListener('submit', async event => {
            event.preventDefault();
            const submit = form.querySelector('[type="submit"]');
            if (submit.disabled) return;
            submit.disabled = true; status(output, '처리 중…');
            try { await callback(form); }
            catch (error) { showError(output, error); }
            finally {
                form.querySelectorAll('input[type="password"]').forEach(input => {input.value = '';});
                submit.disabled = false;
            }
        });
    }
    const login = $('#login-dialog');
    $('#login-open').addEventListener('click', () => login.showModal());
    $('#login-close').addEventListener('click', () => login.close());
    $('#auth-clear').hidden = !token();
    $('#login-open').textContent = token() ? '다시 로그인' : '로그인';
    $('#auth-clear').addEventListener('click', async event => {
        event.currentTarget.disabled = true;
        try {
            await request('/v1/auth/logout', {method:'POST'});
            UI.clearToken(); location.reload();
        } catch (error) {
            if (error.status === 401) { UI.clearToken(); location.reload(); }
            else { login.showModal(); showError($('#login-status'), error); }
        } finally { event.target.disabled = false; }
    });
    bind($('#login-form'), $('#login-status'), async form => {
        const result = await request('/v1/auth/login', json('POST', Object.fromEntries(new FormData(form))), false);
        if (!result?.access_token) throw new Error('로그인 응답을 확인할 수 없습니다.');
        sessionStorage.setItem(UI.key, result.access_token);
        location.reload();
    });
    guestFields();
    const modal = $('#action-dialog'), actionForm = $('#action-form');
    let action = null;
    $('#action-close').addEventListener('click', () => modal.close());
    modal.addEventListener('close', () => { actionForm.reset(); action = null; });
    function confirmAction(title, {content, guest = false, description = '이 작업을 진행할까요?'}, callback) {
        actionForm.reset(); action = callback;
        $('#action-heading').textContent = title;
        $('#action-description').textContent = description;
        $('#action-content-label').hidden = content === undefined;
        actionForm.elements.content.disabled = content === undefined;
        actionForm.elements.content.required = content !== undefined;
        actionForm.elements.content.value = content ?? '';
        $('#action-password-label').hidden = !guest;
        actionForm.elements.guest_password.disabled = !guest;
        actionForm.elements.guest_password.required = guest && !token();
        status($('#action-status'), ''); modal.showModal();
    }
    bind(actionForm, $('#action-status'), async form => {
        const data = {};
        if (!form.elements.content.disabled) data.content = form.elements.content.value;
        if (!form.elements.guest_password.disabled && form.elements.guest_password.value) data.guest_password = form.elements.guest_password.value;
        const callback = action;
        if (callback) { await callback(data); modal.close(); }
    });
    bind($('#signup-form'), $('#page-status'), async form => {
        checkPassword(form.elements.password.value);
        const user = await request('/v1/users', json('POST', Object.fromEntries(new FormData(form))), false);
        form.reset(); status($('#page-status'), `가입 완료 · 회원 ID: ${user.id} · 상단 로그인 버튼으로 로그인해 주세요.`);
    });
    if ($('#password-form')) {
        UI.ready.then(session => {
            const form = $('#password-form');
            if (!session.authenticated) { location.replace('/boards'); return; }
            $('#account-page').hidden = false;
            form.hidden = false;
            form.elements.user_id.value = session.user_id || '';
            form.elements.user_id.readOnly = true;
            if (!session.authenticated) status($('#page-status'), '로그인 후 이용해 주세요.');
        });
        bind($('#password-form'), $('#page-status'), async form => {
            checkPassword(form.elements.new_password.value);
            const id = form.elements.user_id.value.trim();
            await request(`/v1/users/${encodeURIComponent(id)}/password`, json('PATCH', {old_password:form.elements.old_password.value,new_password:form.elements.new_password.value}));
            status($('#page-status'), '비밀번호를 변경했습니다.');
        });
    }
    async function editor() {
        await UI.ready;
        const form = $('#post-form'), id = document.body.dataset.postId;
        let boardId = document.body.dataset.boardId;
        if (id) {
            const post = await request(`/v1/posts/${encodeURIComponent(id)}`);
            if (!UI.canManage(post.author)) { form.hidden = true; throw new Error('본인이 작성한 게시글만 수정할 수 있습니다.'); }
            boardId = post.board_id;
            $('#editor-heading').textContent = '게시글 수정';
            form.elements.title.value = post.title; form.elements.content.value = post.content;
            $('#editor-guest').hidden = true;
            $('#editor-guest').querySelectorAll('input').forEach(input => input.disabled = true);
            $('#edit-password-label').hidden = !post.author.is_guest;
            form.elements.edit_password.required = post.author.is_guest && !token();
            $('#editor-back').href = `/posts/${id}`;
        } else {
            $('#editor-back').href = `/boards/${encodeURIComponent(boardId)}`;
        }
        const board = await request(`/v1/boards/${encodeURIComponent(boardId)}`, {}, false);
        UI.board = board;
        if (!UI.boardAllows('edit_role')) throw new Error('이 게시판에 글을 작성·수정할 권한이 없습니다.');
        form.hidden = false;
        $('#editor-board').textContent = board.board_name;
        form.querySelector('[type="submit"]').disabled = false;
        bind(form, $('#page-status'), async current => {
            const data = {title: current.elements.title.value, content:current.elements.content.value};
            if (id) { if (current.elements.edit_password.value) data.guest_password = current.elements.edit_password.value; }
            else Object.assign(data, guestData(current));
            const post = await request(id ? `/v1/posts/${id}` : `/v1/boards/${encodeURIComponent(boardId)}/posts`, json(id ? 'PUT':'POST', data));
            location.assign(`/posts/${post.post_id}`);
        });
        status($('#page-status'), '');
    }
    async function postActions() {
        await UI.ready;
        const post = UI.post;
        if (!post) return;
        $('#post-actions').hidden = !UI.canManage(post.author) || !UI.boardAllows('edit_role');
        if (!UI.canManage(post.author) || !UI.boardAllows('edit_role')) return;
        $('#post-edit').href = `/posts/${post.post_id}/edit`;
        $('#post-delete').onclick = () => confirmAction('게시글 삭제', {guest:post.author.is_guest,description:'게시글을 삭제합니다. 작성자 또는 관리자 권한이 필요합니다.'}, async data => {
            await request(`/v1/posts/${post.post_id}`, json('DELETE',data));
            location.assign(`/boards/${encodeURIComponent(post.board_id)}`);
        });
    }
    document.addEventListener('board:post-loaded', postActions);
    if (UI.post) postActions();
    async function commentActions() {
        await UI.ready;
        for (const comment of UI.comments || []) {
            const row = $(`[data-comment-id="${comment.comment_id}"]`);
            if (!row || row.querySelector('button') || !UI.canManage(comment.author) || !UI.boardAllows('comment_edit_role')) continue;
            const actions = element('div', 'action-row');
            for (const [label, method] of [['수정','PUT'],['삭제','DELETE']]) {
                const button = element('button', '', label); button.type='button';
                button.onclick = () => confirmAction(`댓글 ${label}`, {guest:comment.author.is_guest,...(method==='PUT'?{content:comment.content}:{})}, async data => {
                    await request(`/v1/comments/${comment.comment_id}`, json(method,data));
                    await UI.loadComments(document.body.dataset.postId);
                }); actions.append(button);
            }
            row.append(actions);
        }
    }
    document.addEventListener('board:comments-loaded', commentActions);
    if (UI.comments) commentActions();
    bind($('#comment-form'), $('#comment-write-status'), async form => {
        await request(`/v1/posts/${document.body.dataset.postId}/comments`, json('POST', {content:form.elements.content.value,...guestData(form)}));
        form.reset(); guestFields(); status($('#comment-write-status'), '댓글을 등록했습니다.');
        await UI.loadComments(document.body.dataset.postId);
    });
    async function manager() {
        const session = await UI.ready;
        if (session.role !== 'ADMIN') {
            location.replace('/boards');
            return;
        }
        $('#manage-page').hidden = false;
        $('#admin-panel').hidden = false;
        const form = $('#board-form'); let selected = null;
        const roles = ['edit_role','view_role','list_role','comment_list_role','comment_edit_role'];
        function reset() { selected=null; form.reset(); form.elements.board_id.readOnly=false; $('#board-delete').hidden=true; $('#manage-heading').textContent='새 게시판'; }
        async function list() {
            const boards = await request(`/v1/boards?include_deleted=${$('#include-deleted').checked}`,{},false);
            $('#manage-list').replaceChildren();
            for (const board of boards) {
                const row = element('li'), button = element('button','',`${board.board_name} / ${board.board_id}`); button.type='button';
                button.onclick = async () => {
                    try {
                        const current = await request(`/v1/boards/${encodeURIComponent(board.board_id)}`,{},false);
                        selected = current.board_id;
                        for (const key of ['board_id','board_name','page_size']) form.elements[key].value=current[key];
                        for (const role of roles) form.elements[role].value=current.authority[role];
                        form.elements.board_id.readOnly=true; $('#board-delete').hidden=false; $('#manage-heading').textContent='게시판 설정 수정';
                        status($('#page-status'),'');
                    } catch(error) { showError($('#page-status'),error); }
                }; row.append(button); $('#manage-list').append(row);
            }
        }
        $('#include-deleted').onchange = () => list().catch(error=>showError($('#page-status'),error));
        $('#manage-new').onclick=reset;
        bind(form, $('#page-status'), async current => {
            const data = {board_name:current.elements.board_name.value,page_size:Number(current.elements.page_size.value),authority:Object.fromEntries(roles.map(role=>[role,current.elements[role].value]))};
            if (!selected) data.board_id=current.elements.board_id.value;
            await request(selected ? `/v1/boards/${encodeURIComponent(selected)}`:'/v1/boards',json(selected?'PUT':'POST',data));
            reset(); await list(); status($('#page-status'),'게시판 설정을 저장했습니다.');
        });
        $('#board-delete').onclick=()=>confirmAction('게시판 삭제', {description:'게시판을 소프트 삭제합니다. 삭제한 ID는 재사용할 수 없습니다.'}, async ()=>{
            await request(`/v1/boards/${encodeURIComponent(selected)}`,{method:'DELETE'});
            reset(); await list(); status($('#page-status'),'게시판을 삭제했습니다.');
        });
        await list();
    }
    if (document.body.dataset.page === 'editor') editor().catch(error=>showError($('#page-status'),error));
    if (document.body.dataset.page === 'manage') manager().catch(error=>showError($('#page-status'),error));
})();
