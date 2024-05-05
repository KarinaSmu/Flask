from datetime import datetime

from fastapi import FastAPI, HTTPException
import databases
import sqlalchemy
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from passlib.context import CryptContext
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


DATABASE_URL = "sqlite:///mydatabase.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


class OrderStatus(str, Enum):
    processing = "processing"
    completed = "completed"
    cancelled = "cancelled"


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String(50)),
    sqlalchemy.Column("last_name", sqlalchemy.String(50)),
    sqlalchemy.Column("email", sqlalchemy.String(128), unique=True),
    sqlalchemy.Column("password", sqlalchemy.String(128))
)


class UserIn(BaseModel):
    first_name: str = Field(..., title="First Name", min_length=3, max_length=50)
    last_name: str = Field(..., title="Last Name", min_length=3, max_length=50)
    email: EmailStr = Field(..., title="Email", max_length=128)
    password: str = Field(..., title="Password", min_length=8)


class User(UserIn):
    id: int


class UserCreate(UserIn):
    @classmethod
    def hash_password(cls, password):
        return pwd_context.hash(password)


async def validate_email_uniqueness(email):
    query = users.select().where(users.c.email == email)
    existing_user = await database.fetch_one(query)
    if existing_user:
        raise ValueError("Email address already exists")
    return email


@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    hashed_password = UserCreate.hash_password(user.password)
    query = users.insert().values(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password
    )
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}


@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    user = await database.fetch_one(query)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/", response_model=List[User])
async def read_users(skip: int = 0, limit: int = 10):
    query = users.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserCreate):
    hashed_password = UserCreate.hash_password(user.password)
    query = users.update().where(users.c.id == user_id).values(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password
    )
    await database.execute(query)
    return {**user.dict(), "id": user_id}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {"message": "User deleted successfully"}


items = sqlalchemy.Table(
    "items",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String(50)),
    sqlalchemy.Column("description", sqlalchemy.String(800)),
    sqlalchemy.Column("price", sqlalchemy.Float(1000000)),
)


class ItemIn(BaseModel):
    title: str = Field(..., title="Item Name", min_length=3, max_length=50)
    description: str = Field(default=None, title="Description", max_length=800)
    price: float = Field(..., title="Price", ge=10, le=1000000)


class ItemCreate(ItemIn):
    pass


class Item(ItemIn):
    id: int


@app.post("/items/", response_model=Item)
async def create_item(item: ItemCreate):
    query = items.insert().values(**item.dict())
    last_record_item_id = await database.execute(query)
    return {**item.dict(), "id": last_record_item_id}


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    query = items.select().where(items.c.id == item_id)
    item = await database.fetch_one(query)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/items/", response_model=List[Item])
async def read_items(skip: int = 0, limit: int = 10):
    query = items.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate):
    query = items.update().where(items.c.id == item_id).values(**item.dict())
    await database.execute(query)
    return {**item.dict(), "id": item_id}


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    query = items.delete().where(items.c.id == item_id)
    await database.execute(query)
    return {"message": "Item deleted successfully"}


orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")),
    sqlalchemy.Column("item_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("items.id")),
    sqlalchemy.Column("order_date", sqlalchemy.DateTime),
    sqlalchemy.Column("status", sqlalchemy.String(50)),
)


class OrderIn(BaseModel):
    user_id: int
    item_id: int
    order_date: datetime = Field(..., title="Order Date")
    status: str


class OrderCreate(OrderIn):
    pass


class Order(OrderIn):
    id: int


@app.post("/orders/", response_model=Order)
async def create_order(order: OrderCreate):
    query = orders.insert().values(**order.dict())
    last_record_order_id = await database.execute(query)
    return {**order.dict(), "id": last_record_order_id}


@app.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int, order=None):
    query = orders.select().where(orders.c.id == order_id)
    order = await database.fetch_one(query)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/orders/", response_model=List[Order])
async def read_orders(skip: int = 0, limit: int = 10):
    query = orders.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {"message": "Order deleted successfully"}


engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)
