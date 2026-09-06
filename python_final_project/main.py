from library_system.specialized_books import Ebook, Paperback
from utils.help import get_string, get_valid_integer


def print_menu():
    print("\n===== 도서 관리 시스템 =====")
    print("1. 도서 등록")
    print("2. 전체 도서 조회")
    print("3. 제목 키워드 검색")
    print("4. 대여/반납 처리")
    print("5. 종료")


def create_book():
    print("\n[1. 도서 등록]")
    print("1. 종이책")
    print("2. 전자책")

    book_type = get_valid_integer("도서 종류를 선택하세요: ", 1, 2)
    title = get_string("제목을 입력하세요: ")
    author = get_string("저자를 입력하세요: ")
    isbn = get_string("ISBN을 입력하세요: ")

    if book_type == 1:
        pages = get_valid_integer("페이지 수를 입력하세요: ", 1)
        return Paperback(title, author, isbn, pages)

    file_size = get_valid_integer("파일 크기(MB)를 입력하세요: ", 1)
    return Ebook(title, author, isbn, file_size)


def main():
    book_catalog = {}

    while True:
        print_menu()
        choice = get_valid_integer("메뉴 번호를 선택하세요: ", 1, 5)

        if choice == 1:
            book = create_book()
            isbn = book.get_isbn()

            if isbn in book_catalog:
                print("이미 등록된 ISBN입니다.")
            else:
                book_catalog[isbn] = book
                print("도서가 등록되었습니다.")

        elif choice == 2:
            print("\n[2. 전체 도서 조회]")

            if not book_catalog:
                print("등록된 도서가 없습니다.")
            else:
                for book in book_catalog.values():
                    print(book.display_info())

        elif choice == 3:
            print("\n[3. 제목 키워드 검색]")
            keyword = get_string("검색할 제목 키워드를 입력하세요: ")
            found = False

            for book in book_catalog.values():
                if keyword in book.get_title():
                    print(book.display_info())
                    found = True

            if not found:
                print("검색 결과가 없습니다.")

        elif choice == 4:
            print("\n[4. 대여/반납 처리]")

            target_isbn = get_string("처리할 도서의 ISBN을 입력하세요: ")

            if target_isbn not in book_catalog:
                print("해당 ISBN을 가진 도서를 찾을 수 없습니다.")
            else:
                target_book = book_catalog[target_isbn]

                if target_book.is_borrowed():
                    target_book.set_borrow_status(False)
                    print(f"도서가 반납되었습니다 - {target_book.get_title()}")
                else:
                    target_book.set_borrow_status(True)
                    print(f"도서가 대여되었습니다 - {target_book.get_title()}")

        elif choice == 5:
            print("\n프로그램을 종료합니다. 감사합니다.")
            break

        else:
            # 메뉴 번호 예외 처리
            print("1~5 사이의 메뉴 번호를 선택하세요.")


if __name__ == "__main__":
    main()
