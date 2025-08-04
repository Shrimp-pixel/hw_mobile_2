from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import ForeignKey, Numeric
from typing import Annotated
from datetime import datetime
from sqlalchemy import func


class Base(DeclarativeBase):
    __abstract__ = True

# id: Mapped[Annotated[int, mapped_column(primary_key=True, comment='Уникальный идентификатор записи')]]


class Genre(Base):
    __tablename__ = 'genre'

    genre_id: Mapped[int] = mapped_column(primary_key=True, comment='Уникальный идентификатор записи')
    name_genre: Mapped[str] = mapped_column(comment='Название', unique=True)

    books: Mapped[list["Book"]] = relationship("Book", back_populates="genre")


class Author(Base):
    __tablename__ = 'author'

    author_id: Mapped[int] = mapped_column(primary_key=True, comment='Уникальный идентификатор записи')
    name_author: Mapped[str] = mapped_column(comment='Название')

    books: Mapped[list["Book"]] = relationship("Book", back_populates="author")


class City(Base):
    __tablename__ = 'city'

    city_id: Mapped[int] = mapped_column(primary_key=True, comment='Уникальный идентификатор записи')
    name_city: Mapped[str] = mapped_column(comment='Название', unique=True)
    days_delivery: Mapped[int] = mapped_column(comment='Время доставки')

    clients: Mapped[list["Client"]] = relationship("Client", back_populates="city")


class Book(Base):
    __tablename__ = 'book'

    book_id: Mapped[int] = mapped_column(primary_key=True, comment='Уникальный идентификатор записи')
    title: Mapped[str] = mapped_column(comment='Название')
    author_id: Mapped[int] = mapped_column(ForeignKey("author.author_id"), comment='id автора')
    genre_id: Mapped[int] = mapped_column(ForeignKey("genre.genre_id"), comment='id жанра')
    price: Mapped[float] = mapped_column(Numeric(scale=2), comment='Время доставки')
    amount: Mapped[int] = mapped_column(comment='Количество на складе')

    author: Mapped["Author"] = relationship("Author", back_populates="books")
    genre: Mapped["Genre"] = relationship("Genre", back_populates="books")
    buy_books: Mapped[list["BuyBook"]] = relationship("BuyBook", back_populates="book")


class Client(Base):
    __tablename__ = 'client'

    client_id: Mapped[int] = mapped_column(primary_key=True, comment='Уникальный идентификатор записи')
    name_client: Mapped[str] = mapped_column(comment='Название')
    city_id: Mapped[int] = mapped_column(ForeignKey("city.city_id"), comment='id города')
    email: Mapped[str] = mapped_column(nullable=False, unique=True, comment='email')

    city: Mapped["City"] = relationship("City", back_populates="clients")
    buys: Mapped[list["Buy"]] = relationship("Buy", back_populates="client")


class Buy(Base):
    __tablename__ = 'buy'

    buy_id: Mapped[int] = mapped_column(primary_key=True, comment='Уникальный идентификатор записи')
    buy_description: Mapped[str] = mapped_column(comment='Описание')
    client_id: Mapped[int] = mapped_column(ForeignKey("client.client_id"), comment='id клиента')

    client: Mapped["Client"] = relationship("Client", back_populates="buys")
    buy_book: Mapped["BuyBook"] = relationship("BuyBook", back_populates="buy")
    buy_step: Mapped["BuyStep"] = relationship("BuyStep", back_populates="buy")


class Step(Base):
    __tablename__ = 'step'

    step_id: Mapped[int] = mapped_column(primary_key=True, comment='Уникальный идентификатор записи')
    name_step: Mapped[str] = mapped_column(comment='Название')

    buy_steps: Mapped[list["BuyStep"]] = relationship("BuyStep", back_populates="step")


class BuyBook(Base):
    __tablename__ = 'buy_book'

    buy_book_id: Mapped[int] = mapped_column(primary_key=True, comment='Уникальный идентификатор записи')
    buy_id: Mapped[int] = mapped_column(ForeignKey("buy.buy_id"), comment='id покупки')
    book_id: Mapped[int] = mapped_column(ForeignKey("book.book_id"), comment='id книги')
    amount: Mapped[int] = mapped_column(comment='Количество')

    buy: Mapped["Buy"] = relationship("Buy", back_populates="buy_book")
    book: Mapped["Book"] = relationship("Book", back_populates="buy_books")


class BuyStep(Base):
    __tablename__ = 'buy_step'

    buy_step_id: Mapped[int] = mapped_column(primary_key=True, comment='Уникальный идентификатор записи')
    buy_id: Mapped[int] = mapped_column(ForeignKey("buy.buy_id"), comment='id покупки')
    step_id: Mapped[int] = mapped_column(ForeignKey("step.step_id"), comment='id шага')
    date_step_beg: Mapped[Annotated[datetime,  mapped_column(server_default=func.now(), comment='Дата начала')]]
    date_step_end: Mapped[Annotated[datetime, mapped_column(comment='Дата окончания')]]

    buy: Mapped["Buy"] = relationship("Buy", back_populates="buy_step")
    step: Mapped["Step"] = relationship("Step", back_populates="buy_steps")

########################################################################################################################


class SpimexTradingResults(Base):
    __tablename__ = "spimex_trading_results"

    id: Mapped[int] = mapped_column(primary_key=True, comment='Уникальный идентификатор записи')
    exchange_product_id: Mapped[str] = mapped_column(comment='Код Инструмента')
    exchange_product_name: Mapped[str] = mapped_column(comment='Имя Инструмента')
    oil_id: Mapped[str] = mapped_column(comment='Id нефти')
    delivery_basis_id: Mapped[str] = mapped_column(comment='Id базиса поставки')
    delivery_basis_name: Mapped[str] = mapped_column(comment='Базис поставки')
    delivery_type_id: Mapped[str] = mapped_column(comment='Id типа доставки')
    volume: Mapped[int] = mapped_column(comment='Объем')
    total: Mapped[int] = mapped_column(comment='Объем Договоров')
    count: Mapped[int] = mapped_column(comment='Количество Договоров')
    date: Mapped[Annotated[datetime,  mapped_column(comment='Дата')]]
    created_on: Mapped[Annotated[datetime,  mapped_column(server_default=func.now(), comment='Дата создания')]]
    updated_on: Mapped[Annotated[datetime,  mapped_column(server_default=func.now(), onupdate=func.now(), comment='Дата обновления')]]


