import orm_db
import yaml
import databases
import sqlalchemy

from dateutil.relativedelta import relativedelta
from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel
from fastapi import FastAPI
from sqlalchemy import select, insert

database_name = 'sqlite'

with open('secrets.yml', 'r') as config:
    secrets = yaml.safe_load(config)

DATABASE_URL = sqlalchemy.engine.URL.create(
    drivername=secrets[database_name]['drivername'],
    username=secrets[database_name]['username'],
    password=secrets[database_name]['password'],
    host=secrets[database_name]['host'],
    database=secrets[database_name]['database'],
)

database = databases.Database(str(DATABASE_URL))

items = orm_db.item
stores = orm_db.store
sales = orm_db.sale

class Item(BaseModel):
    id: int
    name: str
    price: float

class Store(BaseModel):
    id: int
    address: str

class SaleIn(BaseModel):
    id: int
    sale_time: datetime = datetime.now()
    item_id: int
    store_id: int

class SaleShort(BaseModel):
    item_id: int
    store_id: int

class TopStores(BaseModel):
    address: str
    sum_revenue: float

class TopItems(BaseModel):
    name: str
    sum_revenue: float

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/", response_model=Dict)
async def read_root():
    return {"Hello": "World"}


@app.get("/items/", response_model=List[Item])
async def read_item():
    query = select(items)
    return await database.fetch_all(query)

@app.get("/stores/", response_model=List[Store])
async def read_store():
    query = select(stores)
    return await database.fetch_all(query)

@app.get("/stores/top/", response_model=List[TopStores])
async def read_store_top():
    month_ago = datetime.now().date() - relativedelta(month=1)
    query = f'''
        SELECT 
            address,
            SUM(price) as sum_revenue
        FROM
            (SELECT 
                *
            FROM
                stores
            LEFT JOIN (SELECT * FROM sales LEFT JOIN items ON sales.item_id=items.id) as sales ON sales.store_id=stores.id
            WHERE
                sale_time >= {month_ago}
            )
        GROUP BY
            address
        HAVING
            sum_revenue IS NOT NULL
        ORDER BY
            sum_revenue desc
        LIMIT 10
    '''
    return await database.fetch_all(query)

@app.get("/items/top/", response_model=List[TopItems])
async def read_store_top():
    month_ago = datetime.now().date() - relativedelta(month=1)
    query = f'''
        SELECT 
            name,
            SUM(price) as sum_revenue
        FROM
            (SELECT
                *
            FROM
                sales
            LEFT JOIN items ON sales.item_id=items.id
            WHERE
                sale_time >= {month_ago}
            )
        GROUP BY
            name
        HAVING
            sum_revenue IS NOT NULL
        ORDER BY
            sum_revenue desc
        LIMIT 10
    '''
    return await database.fetch_all(query)

@app.post("/sales/", response_model=SaleIn)
async def create_sale(sale_in: SaleShort):
    query = insert(sales).values(item_id=int(sale_in.item_id), store_id=int(sale_in.store_id))
    last_id = await database.execute(query)
    return {**sale_in.dict(), "id": last_id, "sale_time": datetime.now()}
