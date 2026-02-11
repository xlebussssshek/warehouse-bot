import sqlite3
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock(
                   artikul TEXT PRIMARY KEY,
                   name TEXT NOT NULL,
                   quantity INTEGER NOT NULL DEFAULT 0
                   )
                   ''')
    cursor.execute("SELECT COUNT(*) FROM stock")
    if cursor.fetchone()[0] == 0:
        test_data = [
            ('A-001', 'Мышь', '10'),
            ('A-002', 'Клавиатура', '5'),
            ('A-003', 'Монитор', '2'),
        ]
        cursor.executemany("INSERT INTO stock VALUES(?, ?, ?)", test_data)
    conn.commit()
    conn.close()

def get_item(artikul):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity FROM stock WHERE artikul = ?", (artikul,))
    result = cursor.fetchone()
    conn.close()
    return result

def add_quantity(artikul, name, quantity):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
            INSERT INTO stock(artikul, name, quantity)
            VALUES(?, ?, ?)
                      ON CONFLICT(artikul) DO UPDATE SET
                      name = excluded.name,
                      quantity = quantity + excluded.quantity
    ''', (artikul, name, quantity))
    conn.commit()
    conn.close()

def remove_quantity(artikul, quantity):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()


    cursor.execute("SELECT quantity FROM stock WHERE artikul = ?", (artikul,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return False, 'Товар не найден'
    
    current = result[0]
    if current < quantity:
        conn.close()
        return False, f"Недостаточно товара. Доступно: {current}"
    
    cursor.execute(
        "UPDATE stock SET quantity = quantity - ? WHERE artikul = ?",
        (quantity, artikul)
    )

    conn.commit()
    conn.close()
    return True, f"Списано {quantity}. Остаток {current - quantity}"



def get_all_stock():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT artikul, name, quantity FROM stock ORDER BY artikul")
    result = cursor.fetchall()
    conn.close()
    return result


def rename_item(artikul, new_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM stock WHERE artikul = ?", (artikul,))
    if not cursor.fetchone():
        conn.close()
        return False, "Товар не найден"
    
    cursor.execute("UPDATE stock SET name = ? WHERE artikul = ?",
                   (new_name, artikul))
    conn.commit()
    conn.close()
    return True, f"Товар {artikul} переименован в '{new_name}'"


def delete_item(artikul):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM stock WHERE artikul = ?", (artikul,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False, "Товар не найден"
    
    name = result[0]

    cursor.execute("DELETE FROM stock WHERE artikul = ?", (artikul,))
    conn.commit()
    conn.close()
    return True, f"Товар {artikul} - {name} удален со склада"