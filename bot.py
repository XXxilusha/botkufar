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

def load_seen():
    """Читает список ID объявлений, которые уже были отправлены"""
    if os.path.exists(SEEN_PATH):
        with open(SEEN_PATH, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(ids):
    """Сохраняет список ID в файл"""
    with open(SEEN_PATH, "w") as f:
        json.dump(list(ids), f)


# ---------- ЗАГРУЗКА ОБЪЯВЛЕНИЙ С KUFAR ----------

def fetch_ads():
    """Делает запрос к Kufar API и возвращает список объявлений.
    Если сеть не работает — пробует 3 раза с паузой."""

    for attempt in range(3):
        try:
            response = requests.get(KUFAR_API, params=KUFAR_PARAMS, timeout=20)
            data = response.json()
            return data.get("ads", [])
        except Exception:
            print(f"  Попытка {attempt + 1}/3 не удалась")
            if attempt < 2:
                time.sleep(10)
    return []


# ---------- ПАРСИНГ ОДНОГО ОБЪЯВЛЕНИЯ ----------

def parse_ad(raw_ad):
    """Достаёт из сырых данных Kufar нужные поля: id, название, ссылку, описание"""

    # ID объявления
    ad_id = str(raw_ad.get("ad_id", ""))

    # Название
    title = raw_ad.get("subject", "Без названия")

    # Ссылка
    link = raw_ad.get("ad_link", "")
    if not link and ad_id:
        link = f"https://www.kufar.by/item/{ad_id}"

    # Описание (лежит внутри ad_parameters)
    description = ""
    for param in raw_ad.get("ad_parameters", []):
        if param.get("p") == "description":
            description = param.get("vl", "")
            break

    # Обрезаем длинное описание
    if len(description) > 300:
        description = description[:300] + "..."

    return {
        "id": ad_id,
        "title": title,
        "link": link,
        "description": description,
    }


# ---------- ПРОВЕРКА ЧЁРНОГО СПИСКА ----------

def is_blacklisted(ad):
    """Проверяет, содержит ли объявление запрещённые слова (животные и тд)"""
    text = (ad["title"] + " " + ad["description"]).lower()
    for word in BLACKLIST:
        if word in text:
            return True
    return False


# ---------- ОТПРАВКА В TELEGRAM ----------

def send_to_telegram(ad):
    """Формирует красивое сообщение и шлёт в Telegram"""
    message = (
        f"🆓 <b>{ad['title']}</b>\n\n"
        f"{ad['description']}\n\n"
        f"<a href=\"{ad['link']}\">Открыть на Kufar</a>"
    )
    bot.send_message(CHAT_ID, message, parse_mode="HTML")


# ---------- ГЛАВНАЯ ФУНКЦИЯ ----------

def main():
    print("Загрузка объявлений с Kufar...")

    # 1. Загружаем список уже отправленных ID
    seen = load_seen()

    # 2. Получаем свежие объявления с Kufar
    ads = fetch_ads()

    if not ads:
        print("Kufar недоступен. Попробую в следующий раз.")
        return

    # 3. Проходим по каждому объявлению
    new_count = 0
    blocked_count = 0

    for raw_ad in ads:
        ad = parse_ad(raw_ad)

        # Пропускаем если уже отправляли
        if not ad["id"] or ad["id"] in seen:
            continue

        # Пропускаем если в чёрном списке (животные)
        if is_blacklisted(ad):
            blocked_count += 1
            seen.add(ad["id"])
            continue

        # Отправляем в Telegram
        print(f"  Новое: {ad['title']}")
        try:
            send_to_telegram(ad)
            new_count += 1
        except Exception as e:
            print(f"  Ошибка: {e}")

        seen.add(ad["id"])

    # 4. Сохраняем обновлённый список
    save_seen(seen)
    print(f"Готово! Отправлено: {new_count}, заблокировано: {blocked_count}")


# Запуск
if __name__ == "__main__":
    main()
