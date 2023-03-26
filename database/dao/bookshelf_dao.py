from sqlmodel import Session, select
from ..engine import engine
from ..models.bookshelf import Bookshelf
from typing import List


class BookshelfDAO:
    def __init__(self) -> None:
        if not self.bookshelf:
            self.create_initial_bookshelf()

    def read_bookshelf(self):
        with Session(engine) as db:
            bookshelf = db.exec(select(Bookshelf)).all()
            # bookshelf = db.get(Bookshelf)

            return bookshelf
    
    def get_book_title(self, title):
        with Session(engine) as db:
            bookshelf = db.exec(select(Bookshelf).where(Bookshelf.title == title)).all()[0]
            # print("Bookshelf dao", bookshelf)

            return bookshelf

    @property
    def bookshelf(self) -> List[Bookshelf]:
        return self.read_bookshelf()

    # def create_bookshelf(self):
    #     bookshelf = Bookshelf()
    #     with Session(engine) as db:
    #         db.add(bookshelf)
    #         db.commit()
    #         db.refresh(bookshelf)
    #         return bookshelf
    def create_bookshelf(
        self,
        title=None,
        hash=None,
        type=None,
        # length=None,
        indx=0,
        progress=0,
    ):
        bookshelf = Bookshelf()
        with Session(engine) as db:
            if bookshelf:
                if title is not None:
                    bookshelf.title = title
                if hash is not None:
                    bookshelf.hash = hash
                if type is not None:
                    bookshelf.type = type
                if indx is not None:
                    bookshelf.indx = indx
                if progress is not None:
                    bookshelf.progress = progress
                db.add(bookshelf)
                db.commit()
                db.refresh(bookshelf)
                return bookshelf
            else:
                raise ValueError(f"Can't write config")

    def update_title(self, hash, title):
        with Session(engine) as db:
            book = db.exec(select(Bookshelf).where(Bookshelf.hash == hash)).all()[0]
            book.title = title
            db.add(book)
            db.commit()
            db.refresh(book)
            return book
    
    def update_hash(
        self,
        title,
        hash,
        ):
        with Session(engine) as db:
            book = db.exec(select(Bookshelf).where(Bookshelf.title == title)).all()[0]
            book.hash = hash
            book.indx = 0
            book.progress = 0
            db.add(book)
            db.commit()
            db.refresh(book)
            return book
    
    def update_param(
        self,
        title,
        indx=None,
        progress=None,
        ):
        with Session(engine) as db:
            book = db.exec(select(Bookshelf).where(Bookshelf.title == title)).all()[0]
            if book:
                if book.indx is not None:
                    book.indx = indx
                if book.progress is not None:
                    book.progress = progress
                db.add(book)
                db.commit()
                db.refresh(book)
                return book
            else:
                raise ValueError(f"Can't write config")

    def update_bookshelf(
        self,
        title=None,
        hash=None,
        type=None,
        # length=None,
        indx=0,
        progress=0,
    ):
        with Session(engine) as db:
            # bookshelf = db.get(Bookshelf)
            bookshelf = db.exec(select(Bookshelf)).all()[0]
            if bookshelf:
                if title is not None:
                    bookshelf.title = title
                if hash is not None:
                    bookshelf.hash = hash
                if type is not None:
                    bookshelf.type = type
                # if length is not None:
                #     bookshelf.length = length
                if indx is not None:
                    bookshelf.indx = indx
                if progress is not None:
                    bookshelf.progress = progress
                db.add(bookshelf)
                db.commit()
                db.refresh(bookshelf)
                return bookshelf
            else:
                raise ValueError(f"Can't write config")

    def delete_book(self, title: int):
        with Session(engine) as db:
            print("1")
            bookshelf = db.exec(select(Bookshelf).where(Bookshelf.title == title)).all()[0]
            print("2")
            if bookshelf:
                print("3")
                db.delete(bookshelf)
                print("4")
                db.commit()
                print("5")
                return bookshelf
            else:
                raise ValueError(f"Couldn't delete book")
    
    def delete_bookshelf(self):
        with Session(engine) as db:
            bookshelf = db.exec(select(Bookshelf)).all()
            if bookshelf:
                db.delete(bookshelf)
                db.commit()

    def create_initial_bookshelf(self):
        self.create_bookshelf()
