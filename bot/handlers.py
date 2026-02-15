from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from core.config import ALLOWED_USER_IDS
from core.database import get_item, add_quantity, remove_quantity, get_all_stock, rename_item, delete_item, new_item
from excel.excel import create_stock_report
from logger.logger import logger
import re


router = Router()

def check_access(user_id):
    return user_id in ALLOWED_USER_IDS

def log_action(user_id, command, message, **extra):
    message = message.replace("\n", " ")
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
        "**Для существующих товаров:**\n"
        "/add A-001 50 — добавить количество\n"
        "/remove A-001 2 — списать\n\n"
        "**Для новых товаров:**\n"
        "/new A-999 Название товара — создать товар\n\n"
        "**Проверка:**\n"
        "/stock A-001 — узнать остаток\n"
        "/rename A-001 Новое название — переименовать\n"
        "/delete A-001 — удалить товар\n\n"
        "**Отчёты:**\n"
        "/report — выгрузить Excel"
    )

@router.message(Command('stock'))
async def cmd_stock(message : Message):
    user_id = message.from_user.id
    if not check_access(user_id):
        log_action(user_id, "/stock", "доступ запрещён")
        await message.answer("Доступ запрещён")
        return
    

    text = message.text.replace("/stock", "", 1).strip()
    
    artikul = text.upper()
    item = await get_item(artikul)

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
    
    text = message.text.replace("/add", "", 1).strip()
    
    parts = text.rsplit(maxsplit=1)
    
    if len(parts) != 2:
        await message.answer(" Формат: /add A-001 10")
        return
    
    artikul = parts[0].upper()
    try:
        quantity = int(parts[1])
    except ValueError:
        await message.answer("Количество должно быть числом")
        return
    
    if quantity <= 0:
        await message.answer("Число должно быть положительным и не равным нулю")
    
    item = await get_item(artikul)

    if not item:
        log_action(user_id, f"/add {artikul}", "товар не найден")
        await message.answer(f"Товар {artikul} не найден, проверьте артикул или используйте /new для создания")
        return
    
    item_data = await add_quantity(artikul, quantity)

    log_action(user_id, f"/add {artikul} {quantity}", f"успех: новый остаток {item_data}")
    await message.answer(f" Добавлено {quantity} шт.\n{artikul} - {item_data[0]}\nТекущий остаток: {item_data[1]} шт.")

@router.message(Command('remove'))
async def cmd_remove(message : Message):
    user_id = message.from_user.id
    if not check_access(user_id):
        log_action(user_id, "/remove", "доступ запрещён")
        await message.answer("Доступ запрещён")
        return
    
    text = message.text.replace("/remove", "", 1).strip()

    text = text.split()
    if len(text) != 2:
        await message.answer("Формат /remove A-001 2")
        return
    
    artikul = text[0].upper()
    try:
        quantity = int(text[1])
    except ValueError:
        await message.answer("Количество должно быть числом")
        return
    
    success, result = await remove_quantity(artikul, quantity)

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

    data = await get_all_stock()
    filename = create_stock_report(data)

    doc = FSInputFile(filename)
    await message.answer_document(doc, caption=f"Отчет на {filename}")

    log_action(user_id, "/report", f"успех: {filename}")


@router.message(Command('rename'))
async def cmd_rename(message: Message):
    user_id = message.from_user.id
    if not check_access(user_id):
        log_action(user_id, "/rename", "доступ запрещён")
        await message.answer(" Доступ запрещён")
        return
    
    text = message.text.replace("/rename", '', 1).strip()

    parts = text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Формат /rename A-001 Новое название товара")
        return
    
    artikul = parts[0].upper()
    new_name = parts[1]

    success, result = await rename_item(artikul, new_name)

    if success:
        log_action(user_id, f"/rename {artikul}", f"успех: {new_name}")
        await message.answer(f"{result}")

    else:
        log_action(user_id, f"/rename {artikul}", f"ошибка{result}")
        await message.answer(f"{result}")


@router.message(Command('delete'))
async def cmd_delete(message:Message):
    user_id = message.from_user.id
    if not check_access(user_id):
        log_action(user_id, "/delete", "доступ запрещён")
        await message.answer("Доступ запрещён")
        return

    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Формат: /delete A-001")
        return
    
    artikul = parts[1].upper()
    item = await get_item(artikul)

    if not item:
        log_action(user_id, f"/delete {artikul}", "товар не найден")
        await message.answer(f"Товар {artikul} не найден, проверьте артикул")
        return

    await message.answer(f"Точно удалить {artikul}?\n"
                         f"Напишите /confirm_delete {artikul} для подтверждения")
    

@router.message(Command('confirm_delete'))
async def cmd_confirm_delete(message: Message):
    user_id = message.from_user.id
    if not check_access(user_id):
        log_action(user_id, "/confirm_delete", "доступ запрещён")
        await message.answer("Доступ запрещён")
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Формат: /confirm_delete A-001")
        return
    
    artikul = parts[1].upper()

    success, result = await delete_item(artikul)

    if success:
        log_action(user_id, f"/delete {artikul}", f"успех: удален")
        await message.answer(f"{result}")
    else:
        log_action(user_id, f"/delete {artikul}", f"ошибка: {result}")
        await message.answer(f"{result}")


@router.message(Command('new'))
async def cmd_new(message:Message):
    user_id = message.from_user.id
    if not check_access(user_id):
        log_action(user_id, "/new", "доступ запрещён")
        await message.answer("Доступ запрещён")
        return
    text = message.text.replace("/new", "", 1).strip()
    parts = text.split(maxsplit=1)

    if len(parts) != 2:
        await message.answer("Формат: /new A-001 Название товара")
        return
    
    artikul = parts[0].upper()
    name = parts[1]

    success, result = await new_item(artikul, name)
    
    if success:
        log_action(user_id, f"/new {artikul}", f"создан товар {name}")
    else:
        log_action(user_id, f"/new {artikul}", f"ошибка: {result}")
    
    await message.answer(result)