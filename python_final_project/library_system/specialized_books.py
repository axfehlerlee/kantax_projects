# module 2 ibrary_system/ specialized_books.py

from .base_book import Book
# 부모인 Book 가져오기 
# Book에서 상속 받은 자식클래스 Paperback, Ebook 지정하기

class Paperback(Book):
    def __init__(self, title, author, isbn, pages):
        super().__init__(title, author, isbn)
        self.__pages = pages

    def get_pages(self):
        return self.__pages

    def display_info(self):
        return f"{super().display_info()}, 페이지 수: {self.__pages}"


class Ebook(Book):
    def __init__(self, title, author, isbn, file_size):
        super().__init__(title, author, isbn)
        self.__file_size = file_size

    def get_file_size(self):
        return self.__file_size

    def display_info(self):
        return f"{super().display_info()}, 파일 크기: {self.__file_size}MB"
