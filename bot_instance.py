from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from typing import Dict, Any

from handlers import Handlers

class MathHelperBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.user_data: Dict[int, Dict[str, Any]] = {}
        self.handlers = Handlers(self)
        
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        
        self.application.add_handler(CommandHandler("start", self.handlers.start))
        self.application.add_handler(CommandHandler("help", self.handlers.help))
        self.application.add_handler(CommandHandler("solve", self.handlers.solve_equation_command))
        self.application.add_handler(CommandHandler("calc", self.handlers.calc_command))
        self.application.add_handler(CommandHandler("about", self.handlers.about))
        self.application.add_handler(CommandHandler("time", self.handlers.get_time))
        self.application.add_handler(CommandHandler("stats", self.handlers.stats))
        self.application.add_handler(CommandHandler("graph", self.handlers.graph_command))
        
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handlers.handle_text
        ))
    
    def run(self):
        """Запуск бота"""
        self.setup_handlers()
        print("✅ Обработчики настроены")
        print("🤖 Бот запущен. Ожидаю сообщений...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)