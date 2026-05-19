import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8948238511:AAEYX3CjbejSdRThCUSJci6gL4jxjp_9xeA")
CHAT_ID = os.environ.get("CHAT_ID", "955359991")

KUFAR_API_URL = "https://api.kufar.by/search-api/v2/search/rendered-paginated"
KUFAR_PARAMS = {
    "rgn": "7",
    "prc": "r:0,0",
    "size": "50",
    "lang": "ru",
    "sort": "lst.d",
}

SEEN_FILE = "seen_ids.json"

KEYWORDS = {
    "📱 Техника": [
        "iphone", "айфон", "samsung", "самсунг", "galaxy",
        "xiaomi", "сяоми", "redmi", "poco", "huawei", "хуавей",
        "pixel", "oneplus",
        "macbook", "макбук", "ноутбук", "ноут", "laptop",
        "lenovo", "thinkpad", "asus", "acer", "dell", "hp ",
        "видеокарта", "видеокарту", "видюха", "gpu",
        "rtx", "gtx", "geforce", "radeon", "rx 5", "rx 6", "rx 7",
        "процессор", "ryzen", "intel", "core i",
        "монитор", "телевизор",
        "playstation", "ps4", "ps5", "xbox", "nintendo", "switch",
        "ipad", "айпад", "планшет", "tablet",
        "airpods", "наушники", "marshall", "jbl", "sony wh", "bose",
        "apple watch", "часы apple", "garmin", "фитнес",
        "gopro", "камера", "фотоаппарат", "canon", "nikon",
        "ssd", "оперативка", "ddr4", "ddr5",
    ],
    "👔 Бренд-одежда": [
        "gucci", "гуччи", "гучи",
        "balenciaga", "баленсиага", "баленсиаг",
        "rick owens", "рик оуэнс",
        "louis vuitton", "луи витон", "lv ",
        "prada", "прада",
        "dior", "диор",
        "versace", "версаче",
        "burberry", "барберри",
        "off-white", "off white", "оф вайт",
        "stone island", "стоун айленд",
        "moncler", "монклер",
        "canada goose",
        "supreme", "суприм",
        "yeezy", "изи",
        "jordan", "джордан",
        "nike dunk", "nike air", "найк",
        "adidas yeezy", "new balance 550", "new balance 2002",
        "the north face", "норт фейс",
        "arcteryx", "arc'teryx", "арктерикс",
        "palm angels",
        "acne studios",
        "maison margiela", "margiela", "маржела",
        "vetements",
        "chrome hearts", "хром хартс",
    ],
    "💎 Ресейл-находки": [
        "dyson", "дайсон",
        "irobot", "roomba", "робот-пылесос",
        "дрон", "drone", "dji", "mavic",
        "электросамокат", "самокат", "ninebot", "kugoo",
        "велосипед", "giant", "trek", "merida",
        "лего", "lego", "technic",
        "коллекционн", "редк", "винтаж", "антиквар",
        "золот", "серебр", "кольцо", "цепочк", "браслет",
        "гитара", "fender", "gibson", "yamaha",
        "кроссовки", "кеды",
        "сумка", "рюкзак",
        "парфюм", "духи",
        "объектив", "sigma", "tamron",
        "кресло", "herman miller", "ikea markus",
        "mechanical keyboard", "механическ", "keychron",
    ],
}
