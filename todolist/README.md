# My Tasks

Lovable 참고 화면을 바탕으로 만든 개인 Todo 앱입니다. 화면은 Tailwind CSS Play CDN과 `css/style.css`, 동작은 `js/todo.js`에 있습니다.

## 실행

VS Code에서 이 폴더를 열고 `index.html`을 브라우저로 열거나 Live Server로 실행합니다. Tailwind Play CDN을 불러오려면 인터넷 연결이 필요합니다.

## 동작 확인

1. 입력 후 업보 추가 또는 Enter로 등록하면 Backlog에 나타납니다.
2. 하단 가운데 검색창에 단어를 입력하고 조회 또는 Enter를 누르면 해당 단어가 포함된 할 일만 표시됩니다. 영문 대소문자는 구분하지 않으며 검색어를 지우면 전체 목록이 표시됩니다.
3. 말 바꾸기 버튼으로 수정하고 ×로 삭제합니다.
4. 증거 인멸 버튼은 검색 결과와 관계없이 저장된 모든 완료 항목을 삭제합니다.
5. 새로고침 후에도 목록이 남습니다. 브라우저의 localStorage에 저장됩니다. 검색은 저장된 원본을 변경하지 않습니다.
6. 저장된 상태에 따라 세 칸에 표시되며 현재 화면에서 상태를 변경하는 기능은 없습니다. 칸의 숫자는 조회된 개수, 하단 남은 일은 전체 미완료 개수입니다.

제출 폴더 구조는 `jungeun/index.html`, `jungeun/js/todo.js`, `jungeun/css/style.css`입니다. 팀 규칙의 실제 조원 폴더명이 다르면 `jungeun` 폴더 이름만 변경하세요.
