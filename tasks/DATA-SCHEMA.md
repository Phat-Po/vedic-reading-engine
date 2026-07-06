# 数据 Schema — Vedic 卜卦系统

生成日期: 2026-07-06
版本: v1.0（基于 vedic-profile.md 格式规范化）

---

## 设计原则

1. **兼容现有格式** — 与 `vedic-profile.md` 的人工可读格式完全对应
2. **JSON 优先** — 所有计算输出为结构化 JSON，Markdown 仅供人类阅读
3. **完整但可分区** — LLM 解盘时可以只取需要的分区（如只看 D1+Shadbala 而不加载全部），节省 token
4. **精度统一** — 角度用十进制度数（小数点后 6 位），时间用 ISO 8601

---

## 顶层结构

```json
{
  "meta": {},
  "input": {},
  "ayanamsa": {},
  "panchanga": {},
  "sunrise_sunset": {},
  "planets": {},
  "upagrahas": {},
  "special_lagnas": {},
  "houses": {},
  "vargas": {},
  "shadbala": {},
  "ashtakavarga": {},
  "yogas": [],
  "dashas": {},
  "aspects": {},
  "karakas": {}
}
```

---

## 各分区详细 Schema

### 1. meta — 元数据

```json
{
  "meta": {
    "engine": "vedic-divination-engine",
    "version": "1.0.0",
    "swiss_ephemeris_version": "2.10.3",
    "generated_at": "2026-07-06T17:00:00+08:00",
    "calculation_time_ms": 45
  }
}
```

### 2. input — 输入数据

```json
{
  "input": {
    "name": "string | null",
    "birth_date": "1995-07-21",
    "birth_time": "11:35:00",
    "timezone": "Asia/Taipei",
    "utc_offset": "+08:00",
    "latitude": 25.037800,
    "longitude": 121.565000,
    "altitude_m": 0
  }
}
```

### 3. ayanamsa — 岁差设置

```json
{
  "ayanamsa": {
    "system": "sidereal",
    "name": "Lahiri",
    "value_degrees": 23.797701,
    "swisseph_constant": "SIDM_LAHIRI"
  }
}
```

### 4. panchanga — 五支历

```json
{
  "panchanga": {
    "tithi": {
      "name_sanskrit": "Krishna Dashami",
      "name_chinese": "暗月初十",
      "index": 25,
      "start_degrees": 288.00,
      "end_degrees": 300.00,
      "paksha": "krishna",
      "is_shukla": false
    },
    "vara": {
      "name_sanskrit": "Shukravara",
      "name_chinese": "金曜日",
      "index": 6,
      "planet": "Venus"
    },
    "nakshatra": {
      "name_sanskrit": "Bharani",
      "name_chinese": "胃宿",
      "index": 2,
      "start_degrees": 13.33,
      "end_degrees": 26.67,
      "lord": "Venus",
      "pada": 3
    },
    "yoga": {
      "name_sanskrit": "Shula",
      "name_chinese": "首罗",
      "index": 9,
      "start_degrees": 106.67,
      "end_degrees": 120.00
    },
    "karana": {
      "name_sanskrit": "Vanija",
      "name_chinese": "伐尼惹",
      "index": 49,
      "start_degrees": 288.00,
      "end_degrees": 294.00
    }
  }
}
```

### 5. planets — 行星位置

```json
{
  "planets": {
    "sun": {
      "longitude": 94.133333,
      "sign": { "index": 4, "name_en": "Cancer", "name_zh": "巨蟹" },
      "house": 11,
      "degree_in_sign": 4.133333,
      "degree_dms": "4°8'",
      "nakshatra": { "name_en": "Pushya", "name_zh": "鬼宿", "pada": 1, "lord": "Saturn" },
      "retrograde": false,
      "shadbala_total": 0.0,
      "is_combust": false,
      "speed_per_day": 0.953
    },
    "moon": {
      "longitude": 22.933333,
      "sign": { "index": 1, "name_en": "Aries", "name_zh": "白羊" },
      "house": 8,
      "degree_in_sign": 22.933333,
      "degree_dms": "22°56'",
      "nakshatra": { "name_en": "Bharani", "name_zh": "胃宿", "pada": 3, "lord": "Venus" },
      "retrograde": false,
      "shadbala_total": 5.88,
      "is_waxing": false,
      "speed_per_day": 13.2
    },
    "mercury": {},
    "venus": {},
    "mars": {},
    "jupiter": {},
    "saturn": {},
    "uranus": {},
    "neptune": {},
    "pluto": {},
    "rahu": {
      "longitude": 187.800000,
      "sign": { "index": 7, "name_en": "Libra", "name_zh": "天秤" },
      "house": 2,
      "degree_in_sign": 7.800000,
      "degree_dms": "7°48'",
      "nakshatra": { "name_en": "Swati", "name_zh": "亢宿", "pada": 1, "lord": "Rahu" },
      "retrograde": true,
      "is_mean_node": false
    },
    "ketu": {
      "longitude": 7.800000,
      "sign": { "index": 1, "name_en": "Aries", "name_zh": "白羊" },
      "house": 8,
      "degree_in_sign": 7.800000,
      "degree_dms": "7°48'",
      "nakshatra": { "name_en": "Ashwini", "name_zh": "娄宿", "pada": 3, "lord": "Ketu" },
      "retrograde": true,
      "is_mean_node": false
    },
    "ascendant": {
      "longitude": 177.650000,
      "sign": { "index": 6, "name_en": "Virgo", "name_zh": "处女" },
      "house": 1,
      "degree_in_sign": 27.650000,
      "degree_dms": "27°39'",
      "nakshatra": { "name_en": "Chitra", "name_zh": "角宿", "pada": 2, "lord": "Mars" },
      "retrograde": false
    }
  }
}
```

### 6. upagrahas — 虚点

```json
{
  "upagrahas": {
    "dhuma": {
      "longitude": 217.466667,
      "sign": { "index": 8, "name_en": "Scorpio", "name_zh": "天蝎" },
      "house": 3,
      "degree_dms": "17°28'",
      "nakshatra": { "name_en": "Jyeshtha", "name_zh": "心宿", "pada": 1 }
    }
    // Vyatipaata, Parivesha, Indrachaapa, Upaketu,
    // Kaala, Mrityu, ArthaPraharaka, YamaGhantaka,
    // Gulika, Maandi
  }
}
```

### 7. special_lagnas — 特殊上升点

```json
{
  "special_lagnas": {
    "bhava_lagna": {
      "longitude": 187.750000,
      "sign": { "index": 7, "name_en": "Libra", "name_zh": "天秤" },
      "house": 2
    },
    "hora_lagna": {
      "longitude": 281.616667,
      "sign": { "index": 10, "name_en": "Capricorn", "name_zh": "摩羯" },
      "house": 5
    }
    // Ghati Lagna, ViGhati Lagna, Pranapada Lagna,
    // Sree Lagna, Indu Lagna, Varnada Lagna, Kunda,
    // Yogi Point, Avayogi Point
  }
}
```

### 8. houses — 宫位

```json
{
  "houses": {
    "system": "placidus",
    "cusps": {
      "1": { "longitude": 177.65, "sign_index": 6, "sign_name": "Virgo" },
      "2": { "longitude": 205.50, "sign_index": 7, "sign_name": "Libra" },
      "3": { "longitude": 235.20, "sign_index": 8, "sign_name": "Scorpio" },
      "4": { "longitude": 265.10, "sign_index": 9, "sign_name": "Sagittarius" },
      "5": { "longitude": 292.80, "sign_index": 10, "sign_name": "Capricorn" },
      "6": { "longitude": 318.40, "sign_index": 11, "sign_name": "Aquarius" },
      "7": { "longitude": 357.65, "sign_index": 12, "sign_name": "Pisces" },
      "8": { "longitude": 25.50, "sign_index": 1, "sign_name": "Aries" },
      "9": { "longitude": 55.20, "sign_index": 2, "sign_name": "Taurus" },
      "10": { "longitude": 85.10, "sign_index": 3, "sign_name": "Gemini" },
      "11": { "longitude": 112.80, "sign_index": 4, "sign_name": "Cancer" },
      "12": { "longitude": 138.40, "sign_index": 5, "sign_name": "Leo" }
    },
    "bhava_madhya": {},
    "house_lords": {
      "1": "Mercury",
      "2": "Venus",
      "3": "Mars",
      "4": "Jupiter",
      "5": "Saturn",
      "6": "Saturn",
      "7": "Jupiter",
      "8": "Mars",
      "9": "Venus",
      "10": "Mercury",
      "11": "Moon",
      "12": "Sun"
    }
  }
}
```

### 9. vargas — 分盘

```json
{
  "vargas": {
    "d1": {
      "name": "Rasi",
      "description": "主盘 (Main Birth Chart)"
    },
    "d9": {
      "name": "Navamsa",
      "description": "婚姻/伴侣盘",
      "planets": {
        "sun": { "sign_index": 1, "lord": "Mars" },
        "moon": { "sign_index": 5, "lord": "Sun" }
        // ...
      }
    }
    // D2-D60 按需添加
  }
}
```

### 10. shadbala — 六力

```json
{
  "shadbala": {
    "planets": {
      "sun": {
        "sthana_bala": 120.5,
        "dig_bala": 45.0,
        "kala_bala": 98.3,
        "chestha_bala": 40.0,
        "naisargika_bala": 60.0,
        "drik_bala": -12.0,
        "total": 351.8,
        "required": 390.0,
        "is_strong": false,
        "percentage": 90.2
      }
      // moon, mercury, venus, mars, jupiter, saturn
    }
  }
}
```

### 11. ashtakavarga — 八层占

```json
{
  "ashtakavarga": {
    "sav": {
      "description": "Sarvashtakavarga (总合)",
      "houses": { "1": 27, "2": 30, "3": 30, "4": 32, "5": 23, "6": 26, "7": 23, "8": 25, "9": 31, "10": 32, "11": 25, "12": 28 }
    },
    "bav": {
      "sun": { "houses": {} },
      "moon": { "houses": {} }
      // 7 planets each
    },
    "kakshya": {}
  }
}
```

### 12. yogas — 瑜伽

```json
{
  "yogas": [
    {
      "name_sanskrit": "Bhadra Yoga",
      "name_chinese": "贤者瑜伽",
      "category": "pancha_mahapurusha",
      "description_short": "Mercury 在自旺或庙旺星座，形成智者组合",
      "planets_involved": ["Mercury"],
      "strength": "strong"
    },
    {
      "name_sanskrit": "Budha-Aditya Yoga",
      "name_chinese": "水日瑜伽",
      "category": "raja_yoga",
      "description_short": "Mercury 与 Sun 同宫/互视，增强智力与沟通力",
      "planets_involved": ["Mercury", "Sun"],
      "strength": "present"
    }
  ]
}
```

### 13. dashas — 大运

```json
{
  "dashas": {
    "system": "vimshottari",
    "start_lord": "Moon",
    "year_length_days": 365.25,
    "maha_dashas": [
      {
        "lord": "Moon",
        "start_date": "2007-02-15",
        "end_date": "2017-02-15",
        "duration_years": 10,
        "antar_dashas": [
          {
            "lord": "Moon",
            "start_date": "2007-02-15",
            "end_date": "2007-12-15",
            "duration_months": 10
          }
          // ...
        ]
      }
      // Mars, Rahu, Jupiter, Saturn, Mercury, Ketu, Venus, Sun
    ],
    "current": {
      "maha_dasha": "Rahu",
      "maha_dasha_lord": "Rahu",
      "antar_dasha": "Rahu",
      "antar_dasha_lord": "Rahu",
      "pratyantar_dasha": null,
      "start_date": "2024-02-15",
      "end_date": "2026-11-15"
    }
  }
}
```

### 14. aspects — 相位

```json
{
  "aspects": {
    "vedic": {
      "sun": {
        "aspects_to": ["7th_house"],
        "aspected_by": []
      },
      "moon": {
        "aspects_to": ["7th_house"],
        "aspected_by": []
      },
      "mars": {
        "aspects_to": ["4th_house", "7th_house", "8th_house"],
        "aspected_by": ["Saturn"]
      }
      // Mars(4,7,8), Jupiter(5,7,9), Saturn(3,7,10) special aspects
    },
    "western": {}
  }
}
```

### 15. karakas — 指标星

```json
{
  "karakas": {
    "chara_karakas": {
      "mode": "parasara",
      "atmakaraka": { "planet": "Mercury", "degree": 176.083333 },
      "amatya_karaka": { "planet": "Venus", "degree": 175.650000 },
      "bhratri_karaka": { "planet": "Mars", "degree": 156.066667 },
      "matri_karaka": { "planet": "Moon", "degree": 22.933333 },
      "pitri_karaka": { "planet": "Sun", "degree": 94.133333 },
      "putra_karaka": { "planet": "Jupiter", "degree": 221.966667 },
      "jnati_karaka": { "planet": "Rahu", "degree": 187.800000 },
      "dara_karaka": { "planet": "Saturn", "degree": 330.766667 }
    },
    "sthira_karakas": {
      "sun": "Pitri (Father)",
      "moon": "Matri (Mother)",
      "mars": "Bhratri (Sibling)",
      "mercury": "Vidya (Education)",
      "jupiter": "Putra (Children)",
      "venus": "Kalatra (Spouse)",
      "saturn": "Ayush (Longevity)"
    }
  }
}
```

---

## 星座/宫位/Nakshatra 索引表（常量）

```json
{
  "constants": {
    "signs": [
      { "index": 1, "name_en": "Aries", "name_zh": "白羊", "lord": "Mars", "element": "fire", "modality": "movable" },
      { "index": 2, "name_en": "Taurus", "name_zh": "金牛", "lord": "Venus", "element": "earth", "modality": "fixed" },
      { "index": 3, "name_en": "Gemini", "name_zh": "双子", "lord": "Mercury", "element": "air", "modality": "dual" },
      { "index": 4, "name_en": "Cancer", "name_zh": "巨蟹", "lord": "Moon", "element": "water", "modality": "movable" },
      { "index": 5, "name_en": "Leo", "name_zh": "狮子", "lord": "Sun", "element": "fire", "modality": "fixed" },
      { "index": 6, "name_en": "Virgo", "name_zh": "处女", "lord": "Mercury", "element": "earth", "modality": "dual" },
      { "index": 7, "name_en": "Libra", "name_zh": "天秤", "lord": "Venus", "element": "air", "modality": "movable" },
      { "index": 8, "name_en": "Scorpio", "name_zh": "天蝎", "lord": "Mars", "element": "water", "modality": "fixed" },
      { "index": 9, "name_en": "Sagittarius", "name_zh": "射手", "lord": "Jupiter", "element": "fire", "modality": "dual" },
      { "index": 10, "name_en": "Capricorn", "name_zh": "摩羯", "lord": "Saturn", "element": "earth", "modality": "movable" },
      { "index": 11, "name_en": "Aquarius", "name_zh": "水瓶", "lord": "Saturn", "element": "air", "modality": "fixed" },
      { "index": 12, "name_en": "Pisces", "name_zh": "双鱼", "lord": "Jupiter", "element": "water", "modality": "dual" }
    ],
    "nakshatras": [
      { "index": 1, "name_en": "Ashwini", "name_zh": "娄宿", "start_deg": 0.0, "end_deg": 13.33, "lord": "Ketu", "padas": 4 },
      { "index": 2, "name_en": "Bharani", "name_zh": "胃宿", "start_deg": 13.33, "end_deg": 26.67, "lord": "Venus", "padas": 4 },
      { "index": 3, "name_en": "Krittika", "name_zh": "昴宿", "start_deg": 26.67, "end_deg": 40.00, "lord": "Sun", "padas": 4 }
      // ... 共 27 个
    ]
  }
}
```

---

## LLM 解盘时的数据分区策略

LLM 上下文有限，不需要一次性加载全部 JSON。按分析类型取子集：

| 分析类型 | 需要的分区 |
|----------|-----------|
| 本命性格 | planets + houses + nakshatras + karakas + yogas |
| 事业 | planets(D1) + houses + dashas + shadbala + vargas(D10) |
| 感情 | planets(D1) + vargas(D9) + karakas + dashas |
| 投资 | planets + houses(2,5,9,11) + dashas + ashtakavarga |
| 健康 | planets + houses(1,6,8,12) + shadbala |
| 大运总览 | dashas + planets(house_lords) + ashtakavarga |

每个 `calculate` 调用返回完整 JSON，但 `interpret` 调用时选择子集注入 Prompt。
