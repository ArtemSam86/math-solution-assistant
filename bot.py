import logging
import signal
import atexit
from telegram.ext import Application

import config
import database
from process_manager import ProcessManager
from bot_instance import MathHelperBot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    process_manager = ProcessManager('math_bot.pid')
    process_manager.check_existing_process()
    process_manager.create_pid_file()
    process_manager.register_handlers()

    print("=" * 50)
    print("🤖 Math Solution Assistant (версия 0.0.1) запускается...")
    print("=" * 50)

    database.init_db()

    if not config.TOKEN:
        print("❌ Токен бота не найден! Проверьте файл .env")
        logger.error("Токен бота не найден! Проверьте файл .env")
        return

    try:
        bot = MathHelperBot(config.TOKEN)
        print("✅ Бот инициализирован")
        print(f"📊 База данных: {config.DATABASE_NAME}")
        print("🔄 Бот запускается в режиме polling...")
        bot.run()
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        logger.error(f"Ошибка запуска бота: {e}")
    finally:
        print("\n👋 Бот завершает работу...")

if __name__ == '__main__':
    main()