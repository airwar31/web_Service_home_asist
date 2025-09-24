import os

class Config:
    # Flask настройки
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smart-home-secret-key'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Настройки устройств
    DEVICE_LIMITS = {
        'temperature': {'min': 15, 'max': 30},
        'brightness': {'min': 0, 'max': 100},
        'volume': {'min': 0, 'max': 100}
    }
    
    # Настройки голосовых команд
    VOICE_TIMEOUT = 5  # секунд
    VOICE_LANGUAGE = 'ru-RU'
    
    # API настройки
    API_VERSION = 'v1'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}