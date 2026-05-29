import json
import os
import time
import requests
import telebot

# Токен бота и ID чата (берём из переменных окружения или из config)
TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")

if not TOKEN or not CHAT_ID:
    from config import BOT_TOKEN, CHAT_ID as CFG_CHAT
    TOKEN = BOT_TOKEN
    CHAT_ID = CFG_CHAT

# Создаём бота
bot = telebot.TeleBot(TOKEN)

# Путь к файлу где храним ID уже отправленных объявлений
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seen_ids.json")

# Слова-фильтры (животные) — такие объявления пропускаем
bad_words = [
    "кот", "кошк", "котён", "котик", "кошеч",
    "собак", "щенок", "щенк", "пёс", "песик",
    "хомяк", "попугай", "кролик", "черепах",
    "рыбк", "аквариум", "животн", "питомец",
    "корм для", "лоток", "клетк", "птиц",
    "крыс", "шиншилл", "хорёк", "хорек",
    "приют", "передержк", "в добрые руки",
]


# --- Функции ---

# Загружаем список ID которые уже отправляли
def load_seen():
    if os.path.exists(file_path):
        f = open(file_path, "r")
        data = json.load(f)
        f.close()
        return set(data)
    return set()

# Сохраняем список ID в файл
def save_seen(seen):
    f = open(file_path, "w")
    json.dump(list(seen), f)
    f.close()

# Получаем объявления с Kufar API
def get_ads():
    url = "https://api.kufar.by/search-api/v2/search/rendered-paginated"
    params = {
        "rgn": "7",       # Минск
        "prc": "r:0,0",   # бесплатно
        "size": "50",
        "lang": "ru",
        "sort": "lst.d",  # новые первые
    }

    # Пробуем 3 раза если сеть не работает
    for i in range(3):
        try:
            resp = requests.get(url, params=params, timeout=20)
            data = resp.json()
            return data.get("ads", [])
        except:
            print("Не удалось подключиться, попытка", i + 1)
            time.sleep(10)

    return []

# Проверяем есть ли в тексте плохие слова
def is_animal(title, description):
    text = (title + " " + description).lower()
    for word in bad_words:
        if word in text:
            return True
    return False

# Отправляем сообщение в телеграм
def send_message(title, description, link):
    text = "🆓 <b>" + title + "</b>\n\n"
    text = text + description + "\n\n"
    text = text + '<a href="' + link + '">Открыть на Kufar</a>'
    bot.send_message(CHAT_ID, text, parse_mode="HTML")


# --- Главная часть программы ---

print("Загрузка объявлений с Kufar...")

# 1. Загружаем что уже отправляли
seen = load_seen()

# 2. Получаем свежие объявления
ads = get_ads()

if len(ads) == 0:
    print("Kufar недоступен, попробую в следующий раз")
else:
    count = 0

    # 3. Проходим по каждому объявлению
    for ad in ads:

        # Достаём ID
        ad_id = str(ad.get("ad_id", ""))

        # Пропускаем если уже видели
        if ad_id == "" or ad_id in seen:
            seen.add(ad_id)
            continue

        # Достаём название
        title = ad.get("subject", "Без названия")

        # Достаём ссылку
        link = ad.get("ad_link", "")
        if link == "":
            link = "https://www.kufar.by/item/" + ad_id

        # Достаём описание
        description = ""
        for param in ad.get("ad_parameters", []):
            if param.get("p") == "description":
                description = param.get("vl", "")
                break

        # Обрезаем если слишком длинное
        if len(description) > 300:
            description = description[:300] + "..."

        # Пропускаем животных
        if is_animal(title, description):
            seen.add(ad_id)
            continue

        # Отправляем в телеграм
        print("Новое:", title)
        try:
            send_message(title, description, link)
            count = count + 1
        except Exception as e:
            print("Ошибка:", e)

        seen.add(ad_id)

    # 4. Сохраняем
    save_seen(seen)
    print("Готово! Отправлено:", count)
