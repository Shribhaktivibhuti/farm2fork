"""
Constants for FARM2FORK Platform
Predefined crops, varieties, and supported languages
"""

# Predefined crops with varieties
CROPS = {
    "Tomato": ["Cherry", "Beefsteak", "Roma", "Heirloom", "Grape", "Plum"],
    "Potato": ["Russet", "Red", "Yukon Gold", "Fingerling", "Purple", "White"],
    "Onion": ["Red", "White", "Yellow", "Sweet", "Green", "Shallot"],
    "Rice": ["Basmati", "Jasmine", "Arborio", "Brown", "Wild", "Sushi"],
    "Wheat": ["Hard Red", "Soft White", "Durum", "Spelt", "Emmer", "Einkorn"],
    "Carrot": ["Nantes", "Imperator", "Chantenay", "Baby", "Purple", "Rainbow"]
}

# Supported languages for translation
LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi (हिंदी)',
    'ta': 'Tamil (தமிழ்)',
    'te': 'Telugu (తెలుగు)',
    'kn': 'Kannada (ಕನ್ನಡ)',
    'ml': 'Malayalam (മലയാളം)',
    'bn': 'Bengali (বাংলা)',
    'mr': 'Marathi (मराठी)',
    'gu': 'Gujarati (ગુજરાતી)',
    'pa': 'Punjabi (ਪੰਜਾਬੀ)'
}

# Farming methods
FARMING_METHODS = [
    "organic",
    "conventional",
    "integrated"
]

# Treatment types
TREATMENT_TYPES = [
    "pesticide",
    "fertilizer"
]

# Risk level thresholds
RISK_LEVELS = {
    "Safe": (71, 100),
    "Moderate": (41, 70),
    "Risk": (0, 40)
}
