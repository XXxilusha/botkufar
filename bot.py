import json
import os
import time
import requests
import telebot
from config import BOT_TOKEN, CHAT_ID, KUFAR_API_URL, KUFAR_PARAMS, SEEN_FILE, KEYWORDS

bot = telebot.TeleBot(BOT_TOKEN)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEEN_PATH = os.path.join(SCRIPT_DIR, SEEN_FILE)


def load_seen():
    if os.path.exists(SEEN_PATH):
        with open(SEEN_PATH, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_PATH, "w") as f:
        json.dump(list(seen), f)


def fetch_ads():
    for attempt in range(3):
        try:
            resp = requests.get(KUFAR_API_URL, params=KUFAR_PARAMS, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            return data.get("ads", [])
        except (requests.ConnectionError, requests.Timeout) as e:
            print(f"  Попытка {attempt + 1}/3 не удалась: {e}")
            if attempt < 2:
                time.sleep(10)
    return []


def parse_ad(ad):
    ad_id = str(ad.get("ad_id", ""))
    title = ad.get("subject", "Без названия")
    link = ad.get("ad_link", "")
    if not link and ad_id:
        link = f"https://www.kufar.by/item/{ad_id}"

    description = ""
    for param in ad.get("ad_parameters", []):
        if param.get("p") == "description":
            description = param.get("vl", "")
            break

    if len(description) > 300:
        description = description[:300] + "…"

    return {
        "id": ad_id,
        "title": title,
        "link": link,
        "description": description,
    }


def match_keywords(ad):
    text = (ad["title"] + " " + ad["description"]).lower()
    matched = []
    for category, words in KEYWORDS.items():
        for word in words:
            if word.lower() in text:
                matched.append(category)
                break
    return matched


def send_to_telegram(ad, categories):
    tags = " ".join(categories)
    text = (
        f"🆓 {tags}\n"
        f"<b>{ad['title']}</b>\n\n"
        f"{ad['description']}\n\n"
        f"<a href=\"{ad['link']}\">Открыть на Kufar</a>"
    )
    bot.send_message(CHAT_ID, text, parse_mode="HTML", disable_web_page_preview=False)


def main():
    print("Загрузка объявлений с Kufar...")
    seen = load_seen()
    ads = fetch_ads()

    if not ads:
        print("Нет данных (Kufar недоступен или VPN включён). Следующая попытка через 5 мин.")
        return

    new_count = 0
    for ad in ads:
        parsed = parse_ad(ad)
        if not parsed["id"] or parsed["id"] in seen:
            continue

        categories = match_keywords(parsed)
        if not categories:
            seen.add(parsed["id"])
            continue

        print(f"  Новое [{', '.join(categories)}]: {parsed['title']}")
        try:
            send_to_telegram(parsed, categories)
            new_count += 1
        except Exception as e:
            print(f"  Ошибка отправки: {e}")

        seen.add(parsed["id"])

    save_seen(seen)
    print(f"Готово. Отправлено: {new_count}, всего просмотрено: {len(seen)}")


if __name__ == "__main__":
    main()
