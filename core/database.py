from core.config import DB_NAME

from contextlib import asynccontextmanager
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models.stock import Stock, Base
from core.config import PG_URL
from models.transactions import Transaction


engine = create_async_engine(PG_URL, echo=True)
SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
    )

@asynccontextmanager
async def get_session():
    async with SessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with get_session() as session:
        result = await session.execute(select(Stock))
        rows = result.scalars().all()
        
        if len(rows) == 0:
            test_data = [
                Stock(artikul='A-001', name='Мышь', quantity=10),
                Stock(artikul='A-002', name='Клавиатура', quantity=5),
                Stock(artikul='A-003', name='Монитор', quantity=2),
            ]
            session.add_all(test_data)
            await session.commit()
            print("Добавлены тестовые данные")
        else:
            print(f"В базе уже есть {len(rows)} товаров")


async def log_transaction(artikul, type, user_id, quantity=None, old_quantity=None, new_quantity=None, details=None):
    
    async with get_session() as session:
        transaction = Transaction(
            artikul = artikul,
            type = type,
            quantity = quantity,
            old_quantity = old_quantity,
            new_quantity = new_quantity,
            user_id = user_id,
            details = details,
        )

        session.add(transaction)
        await session.commit()


async def get_item(artikul):
    async with get_session() as session:
        result = await session.execute(
                select(Stock).where(Stock.artikul == artikul)
                )
        item = result.scalar_one_or_none()
        return (item.name, item.quantity) if item else None


async def add_quantity(artikul, quantity, user_id):
    async with get_session() as session:
        try:
            result = await session.execute(select(Stock).where(Stock.artikul == artikul))
            item = result.scalar_one()

            if item:
                old_qty = item.quantity
                item.quantity += quantity

            await session.commit()

            
            await log_transaction(
                artikul = artikul,
                type = 'add',
                quantity = quantity,
                old_quantity = old_qty,
                new_quantity = item.quantity,
                user_id = user_id
                )


            return (item.name, item.quantity)
        except Exception as e:
            await session.rollback()
            print(f"Ошибка: {e}")
            return None


async def remove_quantity(artikul, quantity, user_id):
    async with get_session() as session:
        try:
            result = await session.execute(select(Stock).where(Stock.artikul == artikul))
            item = result.scalar_one_or_none()

            if not item:
                return False, "Товар не найден"
            if item.quantity < quantity:
                return False, f"Недостаточно. Доступно: {item.quantity}"
            old_qty = item.quantity
            item.quantity -= quantity
            await session.commit()

            await log_transaction(
                artikul = artikul,
                type = 'remove',
                quantity = quantity,
                old_quantity = old_qty,
                new_quantity = item.quantity,
                user_id = user_id
                )
            
            return True, f"Списано {quantity}. Остаток {item.quantity}"
        except Exception as e:
            await session.rollback()
            return False, f"Ошибка: {e}"


async def get_all_stock():
    async with get_session() as session:
        result = await session.execute(select(Stock).order_by(Stock.artikul))
        items = result.scalars().all()
        return[(item.artikul, item.name, item.quantity) for item in items]
        


async def rename_item(artikul, new_name, user_id):
    async with get_session() as session:
        try:
            result = await session.execute(select(Stock).where(Stock.artikul == artikul))
            item = result.scalar_one_or_none()

            if not item:
                return False, "Товар не найден"
            
            oldname = item.name
            item.name = new_name
            await session.commit()

            await log_transaction(
                artikul = artikul,
                type = 'rename',
                user_id = user_id,
                details= f"Товар {oldname} был переименован в {item.name}"
                )

            return True, f"Товар {artikul} переименован в '{new_name}'"
        except Exception as e:
            await session.rollback()
            return False, f"Ошибка: {e}"



async def delete_item(artikul, user_id):
    async with get_session() as session:
        try:
            result = await session.execute(select(Stock).where(Stock.artikul == artikul))
            item = result.scalar_one_or_none()

            if not item:
                return False, "Товар не найден"
            
            name = item.name
            await session.delete(item)
            await session.commit()

            await log_transaction(
                artikul = artikul,
                type = 'delete',
                user_id = user_id,
                )

            return True, f"Товар {artikul} - {name} удален со склада"
        except Exception as e:
            await session.rollback()
            return False, f"Ошибка: {e}"


async def new_item(artikul, name, user_id):
    async with get_session() as session:
        try:
            result = await session.execute(select(Stock).where(Stock.artikul == artikul))
            existing = result.scalar_one_or_none()

            if existing:
                return False, f"Артикул {artikul} уже существует! Товар: {existing.name}"
            
            existing_by_name = await session.execute(select(Stock).where(func.lower(Stock.name) == func.lower(name)))
            existing_by_name = existing_by_name.scalar_one_or_none()
            if existing_by_name:
                return False, (
                    f"Товар с названием «{name}» уже существует!\n"
                    f"Артикул: {existing_by_name.artikul}\n"
                    f"Название: {existing_by_name.name}\n"
                    f"Остаток: {existing_by_name.quantity}\n\n"
                    f"Используйте этот артикул для добавления товара."
                )

            new_stock = Stock(artikul=artikul, name=name, quantity=0)

            session.add(new_stock)
            await session.commit()

            await log_transaction(
                artikul = artikul,
                type = 'new_item',
                user_id = user_id,
                details=name
                )

            return True, f"Создан новый товар: {artikul} - {name}"
        except Exception as e:
            await session.rollback()
            return False, f"Ошибка при создании товара: {e}"

async def get_history():
    async with get_session() as session:
        result = await session.execute(select(Transaction).order_by(Transaction.id))
        items = result.scalars().all()
        return[(item.id, item.artikul, item.type, item.quantity, item.old_quantity, item.new_quantity, item.user_id, item.details, item.timestamp) for item in items]


