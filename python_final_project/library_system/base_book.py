# module 1 : library_system/ base_book
# 부모인 Book 그래서 from import필요없음 Book 최초로 정의하는 파일이기 때문에
class Book:
    def __init__(self, title, author, isbn):
        self.__title = title
        self.__author = author
        self.__isbn = isbn
        self.__is_borrowed = False

    def get_title(self):
        return self.__title

    def get_author(self):
        return self.__author

    def get_isbn(self):
        return self.__isbn

    def is_borrowed(self):
        return self.__is_borrowed

    def set_borrow_status(self, status):
        self.__is_borrowed = status

    def display_info(self):
        borrow_status = "대여중" if self.__is_borrowed else "대여가능"
        return (
            f"제목: {self.__title}, 저자: {self.__author}, "
            f"ISBN: {self.__isbn}, 상태: {borrow_status}"
        )

    def __str__(self):
        return self.display_info()
