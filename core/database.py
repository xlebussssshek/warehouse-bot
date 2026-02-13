from core.config import DB_NAME


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.stock import Stock, Base

engine = create_engine(f"sqlite:///{DB_NAME}", echo=True)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()


def init_db():
    Base.metadata.create_all(engine)

    session = get_session()
    try:
        count = session.query(Stock).count()

        if count == 0:
            test_data = [
                Stock(artikul = 'A-001', name = 'Мышь', quantity = 10),
                Stock(artikul = 'A-002', name = 'Клавиатура', quantity = 5),
                Stock(artikul = 'A-003', name = 'Монитор', quantity = 2),
            ]

            session.add_all(test_data)
            session.commit()
            print("Добавлены тестовые данные")
        else:
            print(f"В базе уже есть {count} товаров")
    except Exception as e:
        session.rollback()
        print(f"Ошибка инициализации БД: {e}")
    finally:
        session.close()


def get_item(artikul):
    session = get_session()
    try:
        item = session.query(Stock).filter(Stock.artikul == artikul).first()

        if item:
            return (item.name, item.quantity)
        return None
    finally:
        session.close()

def add_quantity(artikul, quantity):
    session = get_session()
    try:
        item = session.query(Stock).filter(Stock.artikul == artikul).first()

        if item:
            item.quantity += quantity

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Ошибка: {e}")
        return None
    finally:
        session.close()


def remove_quantity(artikul, quantity):
    session = get_session()
    try:
        item = session.query(Stock).filter(Stock.artikul == artikul).first()

        if not item:
            return False, "Товар не найден"
        if item.quantity < quantity:
            return False, f"Недостаточно. Доступно: {item.quantity}"
        item.quantity -= quantity
        session.commit()
        return True, f"Списано {quantity}. Остаток {item.quantity}"
    except Exception as e:
        session.rollback()
        return False, f"Ошибка: {e}"
    finally:
        session.close()


def get_all_stock():
    session = get_session()
    try:
        items = session.query(Stock).order_by(Stock.artikul).all()
        return[(item.artikul, item.name, item.quantity) for item in items]
    finally:
        session.close()


def rename_item(artikul, new_name):
    session = get_session()
    try:
        item = session.query(Stock).filter(Stock.artikul == artikul).first()

        if not item:
            return False, "Товар не найден"
            
        item.name = new_name
        session.commit()
        return True, f"Товар {artikul} переименован в '{new_name}'"
    except Exception as e:
        session.rollback()
        return False, f"Ошибка: {e}"
    finally:
        session.close()

def delete_item(artikul):
    session = get_session()
    try:
        item = session.query(Stock).filter(Stock.artikul == artikul).first()

        if not item:
            return False, "Товар не найден"
        
        name = item.name
        session.delete(item)
        session.commit()
        return True, f"Товар {artikul} - {name} удален со склада"
    except Exception as e:
        session.rollback()
        return False, f"Ошибка: {e}"
    finally:
        session.close()




