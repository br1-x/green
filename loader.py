import configparser
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger

# Loglarni sozlash
logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")

def load_config():
    """Config faylidan sozlamalarni yuklash"""
    try:
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        
        if not os.path.exists(config_path):
            logger.error("config.ini fayli topilmadi!")
            exit(1)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config.read_file(f)
        
        # Tokenni to'g'ridan-to'g'ri o'qib, bo'sh joylarni olib tashlash
        token = ''
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('bot_token'):
                    token = line.split('=')[1].strip()
                    break
        
        return {
            'token': token,
            'admin_id': config.get('Settings', 'admin_id', fallback='7712863044'),
            'admin_group': config.get('Settings', 'admin_group', fallback='7712863044')
        }
    except Exception as e:
        logger.error(f"Config faylini o'qishda xatolik: {e}")
        exit(1)

# Sozlamalarni yuklash
config = load_config()

# Token tekshiruvi
if not config['token'] or config['token'] == 'YOUR_BOT_TOKEN_HERE':
    logger.error("Iltimos, config.ini faylida bot_token ni to'g'ri ko'rsating!")
    exit(1)

# Tokendagi bo'sh joylarni olib tashlash
token = config['token'].strip()
logger.debug(f"Token uzunligi: {len(token)}")

try:
    # Botni ishga tushirish
    bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
    storage = MemoryStorage()
    vip = Dispatcher(bot, storage=storage)
    logger.info("Bot muvaffaqiyatli ishga tushirildi")
    
except Exception as e:
    logger.error(f"Botni ishga tushirishda xatolik: {e}")
    exit(1)
