"""Domain constants for sidereal Vedic calculations."""

from __future__ import annotations

SIGNS = [
    {"index": 1, "name_en": "Aries", "name_zh": "白羊", "lord": "Mars"},
    {"index": 2, "name_en": "Taurus", "name_zh": "金牛", "lord": "Venus"},
    {"index": 3, "name_en": "Gemini", "name_zh": "双子", "lord": "Mercury"},
    {"index": 4, "name_en": "Cancer", "name_zh": "巨蟹", "lord": "Moon"},
    {"index": 5, "name_en": "Leo", "name_zh": "狮子", "lord": "Sun"},
    {"index": 6, "name_en": "Virgo", "name_zh": "处女", "lord": "Mercury"},
    {"index": 7, "name_en": "Libra", "name_zh": "天秤", "lord": "Venus"},
    {"index": 8, "name_en": "Scorpio", "name_zh": "天蝎", "lord": "Mars"},
    {"index": 9, "name_en": "Sagittarius", "name_zh": "射手", "lord": "Jupiter"},
    {"index": 10, "name_en": "Capricorn", "name_zh": "摩羯", "lord": "Saturn"},
    {"index": 11, "name_en": "Aquarius", "name_zh": "水瓶", "lord": "Saturn"},
    {"index": 12, "name_en": "Pisces", "name_zh": "双鱼", "lord": "Jupiter"},
]

NAKSHATRAS = [
    ("Ashwini", "娄宿", "Ketu"),
    ("Bharani", "胃宿", "Venus"),
    ("Krittika", "昴宿", "Sun"),
    ("Rohini", "毕宿", "Moon"),
    ("Mrigashira", "觜宿", "Mars"),
    ("Ardra", "参宿", "Rahu"),
    ("Punarvasu", "井宿", "Jupiter"),
    ("Pushya", "鬼宿", "Saturn"),
    ("Ashlesha", "柳宿", "Mercury"),
    ("Magha", "星宿", "Ketu"),
    ("Purva Phalguni", "张宿", "Venus"),
    ("Uttara Phalguni", "翼宿", "Sun"),
    ("Hasta", "轸宿", "Moon"),
    ("Chitra", "角宿", "Mars"),
    ("Swati", "亢宿", "Rahu"),
    ("Vishakha", "氐宿", "Jupiter"),
    ("Anuradha", "房宿", "Saturn"),
    ("Jyeshtha", "心宿", "Mercury"),
    ("Mula", "尾宿", "Ketu"),
    ("Purva Ashadha", "箕宿", "Venus"),
    ("Uttara Ashadha", "斗宿", "Sun"),
    ("Shravana", "女宿", "Moon"),
    ("Dhanishta", "虚宿", "Mars"),
    ("Shatabhisha", "危宿", "Rahu"),
    ("Purva Bhadrapada", "室宿", "Jupiter"),
    ("Uttara Bhadrapada", "壁宿", "Saturn"),
    ("Revati", "奎宿", "Mercury"),
]

VIMSHOTTARI_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

PLANET_IDS = {
    "sun": "SUN",
    "moon": "MOON",
    "mercury": "MERCURY",
    "venus": "VENUS",
    "mars": "MARS",
    "jupiter": "JUPITER",
    "saturn": "SATURN",
    "uranus": "URANUS",
    "neptune": "NEPTUNE",
    "pluto": "PLUTO",
    "rahu": "TRUE_NODE",
}

TITHIS = [
    "Shukla Pratipada", "Shukla Dvitiya", "Shukla Tritiya", "Shukla Chaturthi",
    "Shukla Panchami", "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami",
    "Shukla Navami", "Shukla Dashami", "Shukla Ekadashi", "Shukla Dvadashi",
    "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima", "Krishna Pratipada",
    "Krishna Dvitiya", "Krishna Tritiya", "Krishna Chaturthi", "Krishna Panchami",
    "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami", "Krishna Navami",
    "Krishna Dashami", "Krishna Ekadashi", "Krishna Dvadashi", "Krishna Trayodashi",
    "Krishna Chaturdashi", "Amavasya",
]

VARAS = [
    ("Ravivara", "日曜日", "Sun"),
    ("Somavara", "月曜日", "Moon"),
    ("Mangalavara", "火曜日", "Mars"),
    ("Budhavara", "水曜日", "Mercury"),
    ("Guruvara", "木曜日", "Jupiter"),
    ("Shukravara", "金曜日", "Venus"),
    ("Shanivara", "土曜日", "Saturn"),
]

CLASSICAL_PLANETS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]
GRAHA_KEYS = [*CLASSICAL_PLANETS, "rahu", "ketu"]

PLANET_KEY_TO_NAME = {
    "sun": "Sun",
    "moon": "Moon",
    "mars": "Mars",
    "mercury": "Mercury",
    "jupiter": "Jupiter",
    "venus": "Venus",
    "saturn": "Saturn",
    "rahu": "Rahu",
    "ketu": "Ketu",
}
PLANET_NAME_TO_KEY = {value: key for key, value in PLANET_KEY_TO_NAME.items()}

BENEFICS = {"jupiter", "venus"}
MALEFICS = {"sun", "mars", "saturn", "rahu", "ketu"}

ASPECTS = {
    "sun": [7],
    "moon": [7],
    "mercury": [7],
    "venus": [7],
    "mars": [4, 7, 8],
    "jupiter": [5, 7, 9],
    "saturn": [3, 7, 10],
    "rahu": [5, 7, 9],
    "ketu": [5, 7, 9],
}

EXALTATION = {
    "sun": {"sign": 1, "degree": 10.0},
    "moon": {"sign": 2, "degree": 3.0},
    "mars": {"sign": 10, "degree": 28.0},
    "mercury": {"sign": 6, "degree": 15.0},
    "jupiter": {"sign": 4, "degree": 5.0},
    "venus": {"sign": 12, "degree": 27.0},
    "saturn": {"sign": 7, "degree": 20.0},
}

DEBILITATION = {
    planet: {"sign": ((data["sign"] + 5) % 12) + 1, "degree": data["degree"]}
    for planet, data in EXALTATION.items()
}

MOOLATRIKONA = {
    "sun": 5,
    "moon": 2,
    "mars": 1,
    "mercury": 6,
    "jupiter": 9,
    "venus": 7,
    "saturn": 11,
}

PLANET_FRIENDS = {
    "sun": {"friends": {"moon", "mars", "jupiter"}, "neutrals": {"mercury"}, "enemies": {"venus", "saturn"}},
    "moon": {"friends": {"sun", "mercury"}, "neutrals": {"mars", "jupiter", "venus", "saturn"}, "enemies": set()},
    "mars": {"friends": {"sun", "moon", "jupiter"}, "neutrals": {"venus", "saturn"}, "enemies": {"mercury"}},
    "mercury": {"friends": {"sun", "venus"}, "neutrals": {"mars", "jupiter", "saturn"}, "enemies": {"moon"}},
    "jupiter": {"friends": {"sun", "moon", "mars"}, "neutrals": {"saturn"}, "enemies": {"mercury", "venus"}},
    "venus": {"friends": {"mercury", "saturn"}, "neutrals": {"mars", "jupiter"}, "enemies": {"sun", "moon"}},
    "saturn": {"friends": {"mercury", "venus"}, "neutrals": {"jupiter"}, "enemies": {"sun", "moon", "mars"}},
}

PLANET_GENDER = {
    "sun": "male",
    "moon": "female",
    "mars": "male",
    "mercury": "neutral",
    "jupiter": "male",
    "venus": "female",
    "saturn": "neutral",
}

NAISARGIKA_BALA = {
    "sun": 60.0,
    "moon": 51.43,
    "venus": 42.86,
    "jupiter": 34.29,
    "mercury": 25.71,
    "mars": 17.14,
    "saturn": 8.57,
}

DIG_BALA_HOUSES = {
    "sun": 10,
    "mars": 10,
    "jupiter": 1,
    "mercury": 1,
    "moon": 4,
    "venus": 4,
    "saturn": 7,
}

SHADBALA_COMPONENTS_ZH = {
    "sthana_bala": "位置力",
    "dig_bala": "方向力",
    "kala_bala": "时间力",
    "chestha_bala": "运动力",
    "naisargika_bala": "自然力",
    "drik_bala": "相位力",
}

ODD_SIGNS = {1, 3, 5, 7, 9, 11}
EVEN_SIGNS = {2, 4, 6, 8, 10, 12}
KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}
UPACHAYA_HOUSES = {3, 6, 10, 11}

YOGA_DEFINITIONS = {
    "ruchaka": {"name": "Ruchaka Yoga", "name_zh": "鲁遮迦瑜伽", "category": "pancha-mahapurusha", "planet": "mars"},
    "bhadra": {"name": "Bhadra Yoga", "name_zh": "跋陀罗瑜伽", "category": "pancha-mahapurusha", "planet": "mercury"},
    "hamsa": {"name": "Hamsa Yoga", "name_zh": "汉萨瑜伽", "category": "pancha-mahapurusha", "planet": "jupiter"},
    "malavya": {"name": "Malavya Yoga", "name_zh": "摩罗毗耶瑜伽", "category": "pancha-mahapurusha", "planet": "venus"},
    "sasa": {"name": "Sasa Yoga", "name_zh": "沙沙瑜伽", "category": "pancha-mahapurusha", "planet": "saturn"},
}

VARGA_META = {
    "d1": {"name": "Rasi", "description": "Main birth chart", "weight": 3.5},
    "d2": {"name": "Hora", "description": "Wealth and resources", "weight": 1.0},
    "d3": {"name": "Drekkana", "description": "Siblings, effort, courage", "weight": 1.0},
    "d7": {"name": "Saptamsa", "description": "Children and creativity", "weight": 0.5},
    "d9": {"name": "Navamsa", "description": "Marriage and dharma", "weight": 3.0},
    "d10": {"name": "Dasamsa", "description": "Career and public action", "weight": 1.5},
    "d12": {"name": "Dvadasamsa", "description": "Parents and lineage", "weight": 0.5},
    "d30": {"name": "Trimsamsa", "description": "Challenges and hidden strain", "weight": 1.0},
}


def _bav_rows(*houses: int) -> list[int]:
    return [1 if house in set(houses) else 0 for house in range(1, 13)]


BAV_RULES = {
    "sun": {
        "sun": _bav_rows(1, 2, 4, 7, 8, 9, 10, 11),
        "moon": _bav_rows(3, 6, 10, 11),
        "mars": _bav_rows(1, 2, 4, 7, 8, 9, 10, 11),
        "mercury": _bav_rows(3, 5, 6, 9, 10, 11, 12),
        "jupiter": _bav_rows(5, 6, 9, 11),
        "venus": _bav_rows(6, 7, 12),
        "saturn": _bav_rows(1, 2, 4, 7, 8, 9, 10, 11),
        "ascendant": _bav_rows(3, 4, 6, 10, 11, 12),
    },
    "moon": {
        "sun": _bav_rows(3, 6, 7, 8, 10, 11),
        "moon": _bav_rows(1, 3, 6, 7, 10, 11),
        "mars": _bav_rows(2, 3, 5, 6, 9, 10, 11),
        "mercury": _bav_rows(1, 3, 4, 5, 7, 8, 10, 11),
        "jupiter": _bav_rows(1, 4, 7, 8, 10, 11, 12),
        "venus": _bav_rows(3, 4, 5, 7, 9, 10, 11),
        "saturn": _bav_rows(3, 5, 6),
        "ascendant": _bav_rows(3, 6, 10, 11),
    },
    "mars": {
        "sun": _bav_rows(3, 5, 6, 10, 11),
        "moon": _bav_rows(3, 6, 11),
        "mars": _bav_rows(1, 2, 4, 7, 8, 10, 11),
        "mercury": _bav_rows(3, 5, 6, 11),
        "jupiter": _bav_rows(6, 10, 11, 12),
        "venus": _bav_rows(6, 8, 11, 12),
        "saturn": _bav_rows(1, 4, 7, 8, 9, 10, 11),
        "ascendant": _bav_rows(1, 3, 6, 10, 11),
    },
    "mercury": {
        "sun": _bav_rows(5, 6, 9, 11, 12),
        "moon": _bav_rows(2, 4, 6, 8, 10, 11),
        "mars": _bav_rows(1, 2, 4, 7, 8, 9, 10, 11),
        "mercury": _bav_rows(1, 3, 5, 6, 9, 10, 11, 12),
        "jupiter": _bav_rows(6, 8, 11, 12),
        "venus": _bav_rows(1, 2, 3, 4, 5, 8, 9, 11),
        "saturn": _bav_rows(1, 2, 4, 7, 8, 9, 10, 11),
        "ascendant": _bav_rows(1, 2, 4, 6, 8, 10, 11),
    },
    "jupiter": {
        "sun": _bav_rows(1, 2, 3, 4, 7, 8, 9, 10, 11),
        "moon": _bav_rows(2, 5, 7, 9, 11),
        "mars": _bav_rows(1, 2, 4, 7, 8, 10, 11),
        "mercury": _bav_rows(1, 2, 4, 5, 6, 9, 10, 11),
        "jupiter": _bav_rows(1, 2, 3, 4, 7, 8, 10, 11),
        "venus": _bav_rows(2, 5, 6, 9, 10, 11),
        "saturn": _bav_rows(3, 5, 6, 12),
        "ascendant": _bav_rows(1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    "venus": {
        "sun": _bav_rows(8, 11, 12),
        "moon": _bav_rows(1, 2, 3, 4, 5, 8, 9, 11, 12),
        "mars": _bav_rows(3, 5, 6, 9, 11, 12),
        "mercury": _bav_rows(3, 5, 6, 9, 11),
        "jupiter": _bav_rows(5, 8, 9, 10, 11),
        "venus": _bav_rows(1, 2, 3, 4, 5, 8, 9, 10, 11),
        "saturn": _bav_rows(3, 4, 5, 8, 9, 10, 11),
        "ascendant": _bav_rows(1, 2, 3, 4, 5, 8, 9, 11),
    },
    "saturn": {
        "sun": _bav_rows(1, 2, 4, 7, 8, 10, 11),
        "moon": _bav_rows(3, 6, 11),
        "mars": _bav_rows(3, 5, 6, 10, 11, 12),
        "mercury": _bav_rows(6, 8, 9, 10, 11, 12),
        "jupiter": _bav_rows(5, 6, 11, 12),
        "venus": _bav_rows(6, 11, 12),
        "saturn": _bav_rows(3, 5, 6, 11),
        "ascendant": _bav_rows(1, 3, 4, 6, 10, 11),
    },
}
