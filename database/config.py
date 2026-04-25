"""
Canonical enumerations for the Centific Pricing Intelligence synthetic dataset.
All allowed values live here so every generator stays consistent.
Values come directly from the BRD and TDD schema.
"""

# -------------------------------------------------------------------
# Service catalog â€” each service has a canonical billing unit matching
# the TDD COST_RATES.unit ENUM (per_word / per_hour / per_claim / per_month)
# plus per_minute and per_page used by media & DTP services.
# -------------------------------------------------------------------
SERVICES = {
    "translation":               {"unit": "per_word",   "category": "language"},
    "proofreading":              {"unit": "per_word",   "category": "language"},
    "transcreation":             {"unit": "per_word",   "category": "language"},
    "subtitling":                {"unit": "per_minute", "category": "media"},
    "voiceover":                 {"unit": "per_minute", "category": "media"},
    "dubbing":                   {"unit": "per_minute", "category": "media"},
    "transcription":             {"unit": "per_minute", "category": "media"},
    "interpretation":            {"unit": "per_hour",   "category": "language"},
    "localization_engineering":  {"unit": "per_hour",   "category": "technical"},
    "dtp":                       {"unit": "per_page",   "category": "technical"},
    "qa_testing":                {"unit": "per_hour",   "category": "technical"},
    "content_writing":           {"unit": "per_word",   "category": "content"},
}

# -------------------------------------------------------------------
# BCP-47 locales â€” BR-PI-003 requires this standard.
# -------------------------------------------------------------------
LOCALES = [
    "en-US","en-GB","en-CA","en-AU","en-IN",
    "fr-FR","fr-CA","de-DE","de-AT","es-ES","es-MX","es-AR",
    "it-IT","pt-PT","pt-BR","nl-NL","pl-PL","ru-RU","sv-SE",
    "da-DK","fi-FI","no-NO","cs-CZ","tr-TR","el-GR",
    "zh-CN","zh-TW","ja-JP","ko-KR","th-TH","vi-VN",
    "hi-IN","ta-IN","id-ID","ms-MY",
    "ar-SA","ar-AE","he-IL",
]

# Tier multiplier â€” drives realistic cost variation by market.
LOCALE_TIER = {
    "en-US":1.00,"en-GB":1.05,"en-CA":0.95,"en-AU":1.00,
    "de-DE":1.10,"de-AT":1.08,"fr-FR":1.05,"fr-CA":1.00,
    "ja-JP":1.25,"ko-KR":1.15,"he-IL":1.20,"no-NO":1.15,
    "sv-SE":1.10,"da-DK":1.10,"fi-FI":1.10,"nl-NL":1.05,
    "it-IT":1.00,"es-ES":0.95,"pt-PT":0.95,
    "zh-CN":0.85,"zh-TW":0.90,"pt-BR":0.80,"es-MX":0.75,
    "es-AR":0.70,"pl-PL":0.80,"cs-CZ":0.80,"el-GR":0.85,
    "tr-TR":0.70,"ru-RU":0.75,"ar-SA":0.95,"ar-AE":0.95,
    "en-IN":0.55,"hi-IN":0.50,"ta-IN":0.50,"th-TH":0.65,
    "vi-VN":0.55,"id-ID":0.55,"ms-MY":0.60,
}

# -------------------------------------------------------------------
# Pricing models â€” TDD extracted_data.pricing_model ENUM
# -------------------------------------------------------------------
PRICING_MODELS = ["PER_WORD","PER_HOUR","FIXED","RETAINER","PER_CLAIM","PMPM","TIERED","HYBRID"]

PRICING_MODEL_UNIT_AFFINITY = {
    "per_word":   ["PER_WORD","TIERED","HYBRID"],
    "per_minute": ["FIXED","TIERED","HYBRID","PER_HOUR"],
    "per_hour":   ["PER_HOUR","RETAINER","HYBRID"],
    "per_page":   ["FIXED","PER_WORD","HYBRID"],
}

# -------------------------------------------------------------------
# Base buy-rate anchors (USD) per billing unit â€” market-plausible.
# -------------------------------------------------------------------
BASE_BUY_RATE = {
    "translation":              {"per_word":0.09},
    "proofreading":             {"per_word":0.04},
    "transcreation":            {"per_word":0.18},
    "content_writing":          {"per_word":0.12},
    "subtitling":               {"per_minute":6.50},
    "voiceover":                {"per_minute":14.00},
    "dubbing":                  {"per_minute":28.00},
    "transcription":            {"per_minute":2.20},
    "interpretation":           {"per_hour":65.00},
    "localization_engineering": {"per_hour":55.00},
    "qa_testing":               {"per_hour":40.00},
    "dtp":                      {"per_page":9.00},
}

# -------------------------------------------------------------------
# Supporting enums (TDD schema)
# -------------------------------------------------------------------
RFP_FORMATS   = ["PDF","DOCX","EXCEL","SCANNED"]
RFP_STATUSES  = ["UPLOADED","PROCESSING","EXTRACTED","PRICED","APPROVED","COMPLETED"]
DEAL_STATUSES = ["DRAFT","IN_REVIEW","APPROVED","REJECTED","SUBMITTED"]
USER_ROLES    = ["ANALYST","MANAGER","LEADERSHIP","OPS","COMPLIANCE","ADMIN"]
CURRENCIES    = ["USD","EUR","GBP","INR","JPY","CAD","AUD"]

VOLUME_BANDS = {
    "per_word":   (50_000,   5_000_000),
    "per_minute": (60,       25_000),
    "per_hour":   (40,       8_000),
    "per_page":   (20,       3_000),
}

INDUSTRIES = [
    "Healthcare","Financial Services","Technology","E-commerce",
    "Legal","Manufacturing","Government","Media & Entertainment",
    "Life Sciences","Travel & Hospitality","Education","Automotive",
]

CLIENT_NAME_PARTS = {
    "prefix":["Global","Nexus","Apex","Meridian","Vertex","Prime","North",
              "Atlas","Orion","Sterling","Pinnacle","Horizon","Cascade",
              "Summit","Beacon","Crescent","Fortress","Parallel"],
    "core":  ["Health","Capital","Systems","Logistics","Media","Pharma",
              "Motors","Finance","Networks","Retail","Energy","Dynamics",
              "Partners","Ventures","Technologies","Industries","Analytics"],
    "suffix":["Inc","LLC","Corp","Group","PLC","Holdings","International","Ltd"],
}

FIRST_NAMES = ["Akshat","Lokesh","Rajib","Priya","Arjun","Sneha","Vikram","Meera",
               "Rahul","Anjali","Karthik","Divya","Suresh","Neha","Amit","Kavya",
               "Rohan","Ishita","Nikhil","Pooja","Aditya","Shreya","Varun","Tara",
               "Manish","Ritu","Sanjay","Leela","Harsh","Nisha","Gaurav","Swati",
               "Yash","Ananya","Vivek","Riya","Dev","Sania","Aryan","Zara",
               "Kabir","Myra","Ved","Aisha","Rudra","Diya","Atharv","Kiara",
               "Dhruv","Anika","Reyansh","Saanvi","Vihaan","Aarav","Arya","Advait"]

LAST_NAMES = ["Sharma","Verma","Kumar","Singh","Reddy","Iyer","Menon","Patel",
              "Gupta","Rao","Nair","Basu","Mehta","Joshi","Chopra","Desai",
              "Malhotra","Kapoor","Bhat","Khanna","Cherdup","Bakkireddy",
              "Agarwal","Srinivasan","Banerjee","Chatterjee","Mukherjee"]

# -------------------------------------------------------------------
# Role mix â€” proportional; actual headcount is derived from scale.
# Ratios reflect a real pricing org (many analysts, few admins).
# -------------------------------------------------------------------
ROLE_MIX_RATIO = [
    ("ANALYST",    0.50),
    ("MANAGER",    0.20),
    ("LEADERSHIP", 0.10),
    ("OPS",        0.10),
    ("COMPLIANCE", 0.06),
    ("ADMIN",      0.04),
]

# -------------------------------------------------------------------
# Cost-rate coverage by locale tier & service category.
# Emerging markets have sparser media / technical coverage.
# -------------------------------------------------------------------
COVERAGE_BY_TIER = {
    "high": {"language":0.98, "media":0.90, "technical":0.95, "content":0.92},
    "mid":  {"language":0.95, "media":0.75, "technical":0.85, "content":0.80},
    "low":  {"language":0.90, "media":0.45, "technical":0.65, "content":0.60},
}


def tier_bucket(locale):
    t = LOCALE_TIER[locale]
    if t >= 1.00: return "high"
    if t >= 0.75: return "mid"
    return "low"
