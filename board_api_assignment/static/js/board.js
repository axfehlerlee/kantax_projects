(() => {
    'use strict';
    const key = 'kant_board_access_token';
    const $ = (selector) => document.querySelector(selector);
    function token() { try { return sessionStorage.getItem(key); } catch { return null; } }
    function clearToken() { try { sessionStorage.removeItem(key); } catch {} }
    async function request(url, options = {}, authenticated = true) {
        const headers = new Headers(options.headers);
        if (authenticated && token()) headers.set('Authorization', `Bearer ${token()}`);
        const response = await fetch(url, { ...options, headers });
        if (response.status === 204) return null;
        const body = await response.json().catch(() => null);
        if (!response.ok) {
            const error = new Error(body?.message || (Array.isArray(body?.detail) ? body.detail.map(item => `${item.loc?.slice(1).join('.') || '입력'}: ${item.msg}`).join(' / ') : null) || (typeof body?.detail === 'string' ? body.detail : `요청을 처리하지 못했습니다. (${response.status})`));
            error.status = response.status;
            throw error;
        }
        return body && Object.hasOwn(body, 'data') ? body.data : body;
    }
    function status(element, message, error = false) {
        element.textContent = message;
        element.dataset.error = String(error);
    }
    function showError(element, error) {
        status(element, error.message + (error.status === 401 ? ' 다시 로그인해 주세요.' : error.status === 403 ? ' 이용 권한을 확인해 주세요.' : ''), true);
    }
    function date(value) {
        if (!value) return '—';
        const time = new Date(value);
        return Number.isNaN(time.getTime()) ? '—' : new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'Asia/Seoul' }).format(time);
    }
    function element(tag, className, text) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text !== undefined) node.textContent = text;
        return node;
    }
    const UI = window.BoardUI = { $, token, clearToken, request, status, showError, date, element, key };
    UI.ready = (async () => {
        try {
            UI.session = await request('/ui/session');
        } catch (error) {
            UI.session = { authenticated: false, user_id: null, role: null };
            UI.sessionError = error;
        }
        const session = UI.session;
        document.querySelectorAll('[data-admin-only]').forEach(node => { node.hidden = session.role !== 'ADMIN'; });
        document.querySelectorAll('[data-member-only]').forEach(node => { node.hidden = !session.authenticated; });
        document.querySelectorAll('[data-guest-only]').forEach(node => { node.hidden = session.authenticated; });
        return session;
    })();
    UI.canManage = author => UI.session?.role === 'ADMIN' || (
        UI.session?.authenticated
            ? !!author.author_id && author.author_id === UI.session.user_id
            : !token() && author.is_guest
    );
    UI.allowed = required => {
        if (UI.sessionError) return false;
        const levels = {ALL: 0, USER: 1, ADMIN: 2};
        return Object.hasOwn(levels, required) && (levels[UI.session?.role] ?? 0) >= levels[required];
    };
    UI.boardAllows = key => !!UI.board && UI.allowed(UI.board.authority[key]);
    async function boards() {
        await UI.ready;
        const items = (await request('/v1/boards', {}, false)).filter(board => UI.allowed(board.authority.list_role));
        $('#board-count').textContent = `${items.length}개의 게시판`;
        $('#empty-state').hidden = items.length > 0;
        for (const [index, board] of items.entries()) {
            const li = element('li');
            const link = element('a', 'programme-link');
            link.href = `/boards/${encodeURIComponent(board.board_id)}`;
            const number = element('span', 'programme-index', String(index + 1).padStart(2, '0'));
            number.setAttribute('aria-hidden', 'true');
            const copy = element('span');
            copy.append(element('strong', 'programme-name', board.board_name));
            const permission = board.authority.list_role === 'ALL' ? '누구나 둘러볼 수 있어요' : board.authority.list_role === 'USER' ? '회원 전용 게시판' : '관리자 전용 게시판';
            copy.append(element('small', 'programme-meta', `${board.board_id} · ${permission}`));
            const arrow = element('span', 'programme-arrow', '둘러보기 ↗');
            link.append(number, copy, arrow); li.append(link); $('#board-list').append(li);
        }
        status($('#page-status'), '');
    }
    async function posts() {
        await UI.ready;
        const id = document.body.dataset.boardId;
        const query = new URLSearchParams(location.search);
        const page = Math.max(1, Number.parseInt(query.get('page') || '1', 10) || 1);
        const types = ['ALL', 'TITLE', 'CONTENT', 'TITLE_CONTENT', 'AUTHOR_NAME', 'AUTHOR_EMAIL'];
        const type = types.includes(query.get('search_type')) ? query.get('search_type') : 'ALL';
        $('#search-type').value = type;
        $('#search-keyword').value = query.get('keyword') || '';
        const size = query.get('page_size');
        if (size && /^\d+$/.test(size) && Number(size) >= 1 && Number(size) <= 100) {
            if (![...$('#search-size').options].some(option => option.value === size)) {
                const option = element('option', '', `${size}개`); option.value = size; $('#search-size').append(option);
            }
            $('#search-size').value = size;
        }
        $('.search-form').addEventListener('submit', event => {
            event.preventDefault();
            const next = new URLSearchParams(new FormData(event.currentTarget));
            if (!next.get('page_size')) next.delete('page_size');
            location.assign(`?${next}`);
        });
        const board = await request(`/v1/boards/${encodeURIComponent(id)}`, {}, false);
        UI.board = board;
        $('#post-write-action').hidden = !UI.boardAllows('edit_role');
        if (!UI.boardAllows('list_role')) throw new Error('이 게시판은 현재 권한으로 조회할 수 없습니다.');
        $('#post-list-panel').hidden = false;
        $('#board-name').textContent = board.board_name;
        $('#board-meta').textContent = `${board.board_id} / 한 페이지에 ${board.page_size}개의 이야기`;
        document.title = `${board.board_name} | KANT BOARD`;
        const params = new URLSearchParams({ page: String(page), search_type: type });
        if (query.has('keyword')) params.set('keyword', query.get('keyword'));
        if (size) params.set('page_size', size);
        const data = await request(`/v1/boards/${encodeURIComponent(id)}/posts?${params}`);
        $('#post-count').textContent = `전체 ${data.total_count}개 · 페이지당 ${data.page_size}개`;
        $('#board-meta').textContent = `${board.board_id} / 한 페이지에 ${data.page_size}개의 이야기`;
        $('#empty-state').hidden = data.items.length > 0;
        for (const post of data.items) {
            const row = element('tr');
            const titleCell = element('td', 'post-title');
            const link = element(UI.boardAllows('view_role') ? 'a' : 'span', '', post.title); if (UI.boardAllows('view_role')) link.href = `/posts/${post.post_id}`; titleCell.append(link);
            row.append(element('td', '', String(post.post_id)), titleCell, element('td', '', post.author.author_name), element('td', 'post-date', date(post.created_at)));
            $('#post-list').append(row);
        }
        $('#page-info').textContent = data.total_pages ? `${data.page} / ${data.total_pages} 페이지` : '0개의 페이지';
        for (const [selector, number, visible] of [['#previous', page - 1, page > 1], ['#next', page + 1, page < data.total_pages]]) {
            const link = $(selector); link.hidden = !visible;
            const next = new URLSearchParams(params); next.set('page', String(number)); link.href = `?${next}`;
        }
        status($('#page-status'), '');
    }
    async function detail() {
        const id = document.body.dataset.postId;
        const post = await request(`/v1/posts/${encodeURIComponent(id)}`);
        await UI.ready;
        UI.board = await request(`/v1/boards/${encodeURIComponent(post.board_id)}`, {}, false);
        UI.post = post;
        document.dispatchEvent(new Event('board:post-loaded'));
        $('#post-title').textContent = post.title;
        $('#post-board').textContent = `COMMUNITY / ${post.board_name}`;
        $('#post-meta').textContent = `${post.author.author_name}${post.author.is_guest ? ' · 비회원' : ''} · ${date(post.created_at)}`;
        $('#post-content').textContent = post.content;
        $('#back-to-board').href = `/boards/${encodeURIComponent(post.board_id)}`;
        $('#back-to-board').textContent = `← ${post.board_name}`;
        $('#post-article').hidden = false;
        document.title = `${post.title} | KANT BOARD`;
        status($('#page-status'), '');
        const canList = UI.boardAllows('comment_list_role');
        const canWrite = UI.boardAllows('comment_edit_role');
        $('#comments-section').hidden = !canList && !canWrite;
        $('#comments-heading').hidden = !canList;
        $('#comment-status').hidden = !canList;
        $('#comment-list').hidden = !canList;
        $('#comment-write-panel').hidden = !canWrite;
        if (canList) await loadComments(id);
    }
    async function loadComments(id) {
        try {
            const comments = await request(`/v1/posts/${encodeURIComponent(id)}/comments`);
            UI.comments = comments;
            $('#comment-count').textContent = String(comments.length);
            $('#comment-list').replaceChildren();
            status($('#comment-status'), comments.length ? '' : '아직 댓글이 없습니다.');
            for (const comment of comments) {
                const li = element('li'); li.dataset.commentId = comment.comment_id;
                li.append(element('div', 'comment-meta', `${comment.author.author_name}${comment.author.is_guest ? ' · 비회원' : ''} · ${date(comment.created_at)}`), element('p', '', comment.content));
                $('#comment-list').append(li);
            }
            document.dispatchEvent(new Event('board:comments-loaded'));
        } catch (error) { showError($('#comment-status'), error); }
    }
    UI.loadComments = loadComments;
    const loaders = { boards, posts, detail };
    const load = loaders[document.body.dataset.page];
    if (load) load().catch((error) => showError($('#page-status'), error));
})();
