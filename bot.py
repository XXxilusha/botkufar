import json
import os
import time
import requests
import telebot
from config import BOT_TOKEN, CHAT_ID, KUFAR_API, KUFAR_PARAMS, SEEN_FILE, BLACKLIST


# Создаём бота
bot = telebot.TeleBot(BOT_TOKEN)

# Путь к файлу с уже отправленными объявлениями
SEEN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), SEEN_FILE)


# ---------- РАБОТА С ФАЙЛОМ ДУБЛИКАТОВ ----------

def загрузить_отправленные():
    """Читает список ID объявлений, которые уже были отправлены"""
    if os.path.exists(SEEN_PATH):
        with open(SEEN_PATH, "r") as f:
            return set(json.load(f))
    return set()


def сохранить_отправленные(ids):
    """Сохраняет список ID в файл"""
    with open(SEEN_PATH, "w") as f:
        json.dump(list(ids), f)


# ---------- ЗАГРУЗКА ОБЪЯВЛЕНИЙ С KUFAR ----------

def загрузить_объявления():
    """Делает запрос к Kufar API и возвращает список объявлений.
    Если сеть не работает — пробует 3 раза с паузой."""

    for попытка in range(3):
        try:
            ответ = requests.get(KUFAR_API, params=KUFAR_PARAMS, timeout=20)
            данные = ответ.json()
            return данные.get("ads", [])
        except Exception:
            print(f"  Попытка {попытка + 1}/3 не удалась")
            if попытка < 2:
                time.sleep(10)
    return []


# ---------- ПАРСИНГ ОДНОГО ОБЪЯВЛЕНИЯ ----------

def разобрать_объявление(ad):
    """Достаёт из сырых данных Kufar нужные поля: id, название, ссылку, описание"""

    # ID объявления
    ad_id = str(ad.get("ad_id", ""))

    # Название
    название = ad.get("subject", "Без названия")

    # Ссылка
    ссылка = ad.get("ad_link", "")
    if not ссылка and ad_id:
        ссылка = f"https://www.kufar.by/item/{ad_id}"

    # Описание (лежит внутри ad_parameters)
    описание = ""
    for param in ad.get("ad_parameters", []):
        if param.get("p") == "description":
            описание = param.get("vl", "")
            break

    # Обрезаем длинное описание
    if len(описание) > 300:
        описание = описание[:300] + "..."

    return {
        "id": ad_id,
        "title": название,
        "link": ссылка,
        "description": описание,
    }


# ---------- ПРОВЕРКА ЧЁРНОГО СПИСКА ----------

def в_чёрном_списке(объявление):
    """Проверяет, содержит ли объявление запрещённые слова (животные и тд)"""
    текст = (объявление["title"] + " " + объявление["description"]).lower()
    for слово in BLACKLIST:
        if слово in текст:
            return True
    return False


# ---------- ОТПРАВКА В TELEGRAM ----------

def отправить_в_телеграм(объявление):
    """Формирует красивое сообщение и шлёт в Telegram"""
    сообщение = (
        f"🆓 <b>{объявление['title']}</b>\n\n"
        f"{объявление['description']}\n\n"
        f"<a href=\"{объявление['link']}\">Открыть на Kufar</a>"
    )
    bot.send_message(CHAT_ID, сообщение, parse_mode="HTML")


# ---------- ГЛАВНАЯ ФУНКЦИЯ ----------

def main():
    print("Загрузка объявлений с Kufar...")

    # 1. Загружаем список уже отправленных ID
    отправленные = загрузить_отправленные()

    # 2. Получаем свежие объявления с Kufar
    объявления = загрузить_объявления()

    if not объявления:
        print("Kufar недоступен. Попробую в следующий раз.")
        return

    # 3. Проходим по каждому объявлению
    новых = 0
    заблокировано = 0

    for ad in объявления:
        объявление = разобрать_объявление(ad)

        # Пропускаем если уже отправляли
        if not объявление["id"] or объявление["id"] in отправленные:
            continue

        # Пропускаем если в чёрном списке (животные)
        if в_чёрном_списке(объявление):
            заблокировано += 1
            отправленные.add(объявление["id"])
            continue

        # Отправляем в Telegram
        print(f"  Новое: {объявление['title']}")
        try:
            отправить_в_телеграм(объявление)
            новых += 1
        except Exception as e:
            print(f"  Ошибка: {e}")

        отправленные.add(объявление["id"])

    # 4. Сохраняем обновлённый список
    сохранить_отправленные(отправленные)
    print(f"Готово! Отправлено: {новых}, заблокировано: {заблокировано}")


# Запуск
if __name__ == "__main__":
    main()
