from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from config import ALLOWED_USER_IDS
from database import get_item, add_quantity, remove_quantity, get_all_stock
from excel import create_stock_report
from logger import logger
import re


router = Router()

def check_access(user_id):
    return user_id in ALLOWED_USER_IDS

def log_action(user_id, command, message, **extra):
    logger.info(
        "",
        extra ={
            "user_id" : user_id,
            "command" : command,
            "text" : message
        }
    )

@router.message(Command('start'))
async def cmd_start(message : Message):
    user_id = message.from_user.id
    if not check_access(user_id):
        log_action(user_id, '/start', 'доступ запрещен')
        await message.answer("Доступ запрещен")
        return
    

    log_action(user_id, '/start', 'успех')
    await message.answer(
        "Добро пожаловать!\n\n"
        "/stock A-001 — узнать остаток\n"
        "/add A-001 Мышь 10 — добавить товар\n"
        "/remove A-001 2 — списать\n"
        "/report — выгрузить Excel"
    )

@router.message(Command('stock'))
async def cmd_stock(message : Message):
    user_id = message.from_user.id
    if not check_access(user_id):
        log_action(user_id, "/stock", "доступ запрещён")
        await message.answer("Доступ запрещён")
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Формат: /stock A-001")
        return
    
    artikul = parts[1].upper()
    item = get_item(artikul)

    if not item:
        log_action(user_id, f"/stock {artikul}", "товар не найден")
        await message.answer(f"Товар {artikul} не найден")
        return
    
    name, quantity = item
    log_action(user_id, f"/stock {artikul}", f"успех: {quantity} шт.")
    await message.answer(f"{artikul} - {name}\nОстаток: {quantity} шт.")


@router.message(Command("add"))
async def cmd_add(message: Message):
    user_id = message.from_user.id
    if not check_access(user_id):
        log_action(user_id, "/add", "доступ запрещён")
        await message.answer("Доступ запрещён")
        return
    
    # Получаем текст после команды
    text = message.text.replace("/add", "", 1).strip()
    
    # Ищем ПОСЛЕДНЕЕ число — это количество
    parts = text.rsplit(maxsplit=1)
    
    if len(parts) != 2:
        await message.answer(" Формат: /add A-001 Название товара 10")
        return
    
    name_with_artikul = parts[0].strip()  # "A-001 Офисная мышь"
    try:
        quantity = int(parts[1])  # "10" -> 10
    except ValueError:
        await message.answer(" Количество должно быть числом")
        return
    
    # Разделяем артикул и название
    name_parts = name_with_artikul.split(maxsplit=1)
    if len(name_parts) != 2:
        await message.answer(" Укажите артикул и название")
        return
    
    artikul = name_parts[0].upper()
    name = name_parts[1]  # Всё, что после артикула — название
    
    add_quantity(artikul, name, quantity)
    new_qty = get_item(artikul)[1]
    
    log_action(user_id, f"/add {artikul} {quantity}", f"успех: новый остаток {new_qty}")
    await message.answer(f" Добавлено {quantity} шт.\n{artikul} - {name}\nТекущий остаток: {new_qty} шт.")

@router.message(Command('remove'))
async def cmd_remove(message : Message):
    user_id = message.from_user.id
    if not check_access(user_id):
        log_action(user_id, "/remove", "доступ запрещён")
        await message.answer("Доступ запрещён")
        return
    
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Формат /remove A-001 2")
        return
    
    artikul = parts[1].upper()
    try:
        quantity = int(parts[2])
    except ValueError:
        await message.answer("Количество должно быть числом")
        return
    
    success, result = remove_quantity(artikul, quantity)

    if success:
        log_action(user_id, f"/remove {artikul} {quantity}", f"успех {result}")
        await message.answer(f"{result}")

    else:
        log_action(user_id, f"/remove {artikul} {quantity}", f"ошибка: {result}")
        await message.answer(f"{result}")

@router.message(Command('report'))
async def cmd_report(message: Message):
    user_id = message.from_user.id
    if not check_access(user_id):
        log_action(user_id, "/report", "доступ запрещён")
        await message.answer(" Доступ запрещён")
        return
    
    await message.answer("Генерирую отчет")

    data = get_all_stock()
    filename = create_stock_report(data)

    doc = FSInputFile(filename)
    await message.answer_document(doc, caption=f"Отчет на {filename}")

    log_action(user_id, "/report", f"успех: {filename}")
