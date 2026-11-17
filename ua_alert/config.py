"""Application constants and region names."""
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path.home() / ".ua-alert" / "history.sqlite3"
API_URL = "https://api.alerts.in.ua/v1/alerts/active.json"
REFRESH_SECONDS = 30
STALE_AFTER_SECONDS = 120
DISCLAIMER = ("UA Alert is an auxiliary information tool. It does not replace official air raid alerts, "
              "emergency services, sirens, or instructions from Ukrainian authorities. Always follow official emergency guidance.")

# UIDs used by Alerts.in.ua for oblast-level records where known.
REGIONS = [
    ("29", "Автономна Республіка Крим", "Autonomous Republic of Crimea"), ("8", "Волинська область", "Volyn Oblast"),
    ("4", "Вінницька область", "Vinnytsia Oblast"), ("9", "Дніпропетровська область", "Dnipropetrovsk Oblast"),
    ("28", "Донецька область", "Donetsk Oblast"), ("10", "Житомирська область", "Zhytomyr Oblast"),
    ("11", "Закарпатська область", "Zakarpattia Oblast"), ("12", "Запорізька область", "Zaporizhzhia Oblast"),
    ("13", "Івано-Франківська область", "Ivano-Frankivsk Oblast"), ("14", "Київська область", "Kyiv Oblast"),
    ("15", "Кіровоградська область", "Kirovohrad Oblast"), ("16", "Луганська область", "Luhansk Oblast"),
    ("27", "Львівська область", "Lviv Oblast"), ("17", "Миколаївська область", "Mykolaiv Oblast"),
    ("18", "Одеська область", "Odesa Oblast"), ("19", "Полтавська область", "Poltava Oblast"),
    ("5", "Рівненська область", "Rivne Oblast"), ("20", "Сумська область", "Sumy Oblast"),
    ("21", "Тернопільська область", "Ternopil Oblast"), ("22", "Харківська область", "Kharkiv Oblast"),
    ("23", "Херсонська область", "Kherson Oblast"), ("3", "Хмельницька область", "Khmelnytskyi Oblast"),
    ("24", "Черкаська область", "Cherkasy Oblast"), ("26", "Чернівецька область", "Chernivtsi Oblast"),
    ("25", "Чернігівська область", "Chernihiv Oblast"), ("31", "м. Київ", "Kyiv City"),
]
