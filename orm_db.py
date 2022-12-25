import yaml
from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column, Integer, String, Float, DateTime, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, Session, relationship
from sqlalchemy.engine import URL
from sqlalchemy.sql import func

database_name = 'sqlite'

Base = declarative_base()
# class Base(Table):
#     pass

class store(Base):
    __tablename__ = 'stores'

    id: Mapped[int] = Column(Integer, primary_key=True , autoincrement=True, comment="Идентификатор магазина")
    address: Mapped[str] = Column(String(300), comment="Адрес магазина")
    sale = relationship('sale')

    def __repr__(self) -> str:
        return f'store(id={self.id!r}, address={self.address!r})'

class item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = Column(Integer, primary_key=True , autoincrement=True, comment="Идентификатор товарной позиции")
    name: Mapped[str] = Column(String(150), unique=True, comment="Уникальное наименование товара")
    price: Mapped[float] = Column(Float, comment='Цена товарной позиции')
    sale = relationship('sale')

    def __repr__(self) -> str:
        return f'item(id={self.id!r}, name={self.name!r}, price={self.price:.2f})'

class sale(Base):
    __tablename__ = 'sales'

    id: Mapped[int] = Column(Integer, primary_key=True , autoincrement=True, comment="Идентификатор продажи")
    sale_time: Mapped[DateTime] = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    item_id: Mapped[int] = Column(ForeignKey('items.id'), comment="Id товара из таблицы items")
    store_id: Mapped[int] = Column(ForeignKey('stores.id'), comment="Id магазина из таблицы stores")

    def __repr__(self) -> str:
        return f'sale(id={self.id!r}, sale_time={self.sale_time!r})'

def make_engine():
    with open('secrets.yml', 'r') as config:
        secrets = yaml.safe_load(config)

    url_object = URL.create(
        drivername=secrets[database_name]['drivername'],
        username=secrets[database_name]['username'],
        password=secrets[database_name]['password'],
        host=secrets[database_name]['host'],
        database=secrets[database_name]['database'],
    )

    engine = create_engine(url_object, echo=True)
    return engine

def main():
    engine = make_engine()
    Base.metadata.create_all(engine)
    
    with Session(engine) as session:

        test_bd_items_list = [
            store(address='test_Н-ск, ул. Тестовая, д. 1'),
            store(address='test_ул. Мира д. 150'),
            store(address='test_Н-ск, ул. Тверская, д. 15'),
            item(name='test_Vacuumcleaner', price=5032.78),            
            item(name='test_TestItem', price=1.11),
            item(name='test_Iphone14', price=100000),
            sale(item_id=1, store_id=2),
            sale(item_id=1, store_id=1),            
            sale(sale_time=datetime(2022, 1, 1, 13, 5, 47), item_id=2, store_id=1),
            sale(sale_time=datetime(2022, 1, 15, 13, 5, 47), item_id=1, store_id=3),
            sale(sale_time=datetime(2022, 1, 25, 13, 5, 47), item_id=3, store_id=2),
            sale(sale_time=datetime(2022, 3, 25, 13, 5, 47), item_id=3, store_id=1),
            sale(item_id=1, store_id=1),
            sale(item_id=1, store_id=2),
            sale(item_id=1, store_id=3),
            sale(item_id=1, store_id=3),
        ]

        session.add_all(test_bd_items_list)
        session.commit()

if __name__ == "__main__":
    main()