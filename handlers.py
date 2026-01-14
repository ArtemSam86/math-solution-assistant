from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from datetime import datetime
import pytz
import io

import database
from keyboards import get_main_keyboard, get_calc_keyboard, get_graph_keyboard
from services import Services
from message_formatter import MessageFormatter

class Handlers:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.services = Services()
        self.formatter = MessageFormatter()
        
        self.button_actions = {
            "🧮 Решить уравнение": self.solve_equation_start,
            "📊 Построить график": self.graph_start,
            "🔢 Калькулятор": self.calc_start,
            "🕐 Текущее время": self.get_time,
            "📚 Помощь": self.help,
            "ℹ️ О боте": self.about,
            "📊 Статистика": self.stats,
            "❌ Скрыть клавиатуру": self.hide_keyboard,
            "⬅️ Назад": self.back_to_main,
            "=": self.calc_evaluate,
            "🔢 Вычислить": self.calc_evaluate,
            "C": self.calc_clear,
            "⌫": self.calc_backspace,
            "📈 Построить": self.graph_draw
        }
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        if user.id in self.bot.user_data:
            self.bot.user_data[user.id] = {'mode': 'main'}
        
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\nЯ бот-помощник по математике.\n\n"
            "Выберите действие на клавиатуре ниже ⬇️",
            reply_markup=get_main_keyboard()
        )
        
        database.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        database.log_command(user.id, "start")
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
             🤖 **Math Helper Bot - Помощь**

**Основные команды:**
/start - Начать работу с ботом
/help - Показать это сообщение
/about - Информация о боте
/stats - Статистика использования

**Математические функции:**
/solve <уравнение> - Решить уравнение
    Примеры:
    • /solve 2*x + 5 = 15
    • /solve x**2 - 4 = 0
    • /solve sin(x) = 0.5

/graph <функция> - Построить график
    Примеры:
    • /graph x^2
    • /graph sin(x)*cos(x)
    • /graph exp(-x^2/2)

/calc <выражение> - Калькулятор
    Пример:
    • /calc 2+2*2

**Или используйте кнопки на клавиатуре!** ⬇️
            """
        # await update.message.reply_text(
        #     help_text,
        #     parse_mode='Markdown',
        #     reply_markup=get_main_keyboard()
        # )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=help_text,  # Текст в выбранном формате
            parse_mode='Markdown'  # Или 'HTML', или 'MarkdownV2'
        )
        database.log_command(update.effective_user.id, "help")
    
    async def solve_equation_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало режима решения уравнений"""
        user_id = update.effective_user.id
        self.bot.user_data[user_id] = {'mode': 'solve'}
        
        await update.message.reply_text(
            "🧮 <b>Решатель уравнений</b>\n\n"
            "Введите уравнение для решения.\n\n"
            "<b>Примеры:</b>\n"
            "• 2*x + 5 = 15\n"
            "• x**2 - 4 = 0\n"
            "• sin(x) = 0.5\n"
            "• x^3 - 2*x^2 + x - 1 = 0\n"
            "• exp(x) = 10\n"
            "• log(x) = 2\n\n"
            "Для возврата нажмите '⬅️ Назад'.",
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
    
    async def solve_equation_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /solve"""
        if not context.args:
            await update.message.reply_text(
                "Введите уравнение после команды /solve\n"
                "Пример: /solve 2*x + 5 = 15"
            )
            return
        
        equation = ' '.join(context.args)
        await self._solve_equation(update, equation)
    
    async def _solve_equation(self, update: Update, equation: str):
        """Решение уравнения"""
        user_id = update.effective_user.id
        
        try:
            await update.message.reply_text(
                f"🔍 Решаю уравнение: {equation}\n"
                "Пожалуйста, подождите..."
            )
            
            result = self.services.solver.solve(equation)
            
            if result['error']:
                await update.message.reply_text(result['error_message'], parse_mode='HTML')
            else:
                response = self.formatter.format_equation_solution(result)
                await update.message.reply_text(response, parse_mode='HTML')
            
            database.log_message(
                user_id,
                f"solve: {equation}",
                f"solutions: {result.get('solutions', [])}"
            )
            
            await update.message.reply_text(
                "Что вы хотите сделать дальше?",
                reply_markup=get_main_keyboard()
            )
            
            if user_id in self.bot.user_data:
                self.bot.user_data[user_id]['mode'] = 'main'
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)[:200]}")
    
    async def graph_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало режима построения графиков"""
        user_id = update.effective_user.id
        self.bot.user_data[user_id] = {'mode': 'graph', 'function': ''}
        
        await update.message.reply_text(
            "📊 <b>Построитель графиков</b>\n\n"
            "Введите функцию для построения графика.\n"
            "Или выберите пример из кнопок ниже.\n\n"
            "Для возврата нажмите '⬅️ Назад'.",
            parse_mode='HTML',
            reply_markup=get_graph_keyboard()
        )
    
    async def graph_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /graph"""
        if not context.args:
            await self.graph_start(update, context)
            return
        
        func_str = ' '.join(context.args)
        await self._draw_graph(update, func_str)
    
    async def graph_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода функции для графика"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id not in self.bot.user_data:
            self.bot.user_data[user_id] = {'mode': 'graph', 'function': ''}
        
        examples = {
            "x^2": "x**2",
            "sin(x)": "sin(x)",
            "cos(x)": "cos(x)",
            "e^x": "exp(x)",
            "ln(x)": "log(x)",
            "√(x)": "sqrt(x)",
            "1/x": "1/x",
            "|x|": "abs(x)",
            "x^3": "x**3"
        }
        
        if text in examples:
            self.bot.user_data[user_id]['function'] = examples[text]
            func_display = text
        else:
            self.bot.user_data[user_id]['function'] = text
            func_display = text
        
        await update.message.reply_text(
            f"📝 Функция: {func_display}\n\n"
            "Нажмите '📈 Построить' для создания графика.\n"
            "Или введите другую функцию.",
            parse_mode='HTML',
            reply_markup=get_graph_keyboard()
        )
    
    async def graph_draw(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Построение графика"""
        user_id = update.effective_user.id
        
        if user_id not in self.bot.user_data or 'function' not in self.bot.user_data[user_id]:
            await update.message.reply_text(
                "❌ Сначала введите функцию",
                reply_markup=get_graph_keyboard()
            )
            return
        
        func_str = self.bot.user_data[user_id]['function']
        
        if not func_str:
            await update.message.reply_text(
                "❌ Функция не указана",
                reply_markup=get_graph_keyboard()
            )
            return
        
        try:
            await update.message.reply_text(
                f"📈 Строю график функции: {func_str}\n"
                "Пожалуйста, подождите..."
            )
            
            result = self.services.plotter.create_graph(func_str)
            
            if result is None:
                await update.message.reply_text(
                    "❌ Не удалось построить график.\n"
                    "Проверьте правильность функции.",
                    reply_markup=get_graph_keyboard()
                )
                return
            
            buf, info = result
            caption = self.formatter.format_graph_info(
                func_str, 
                info['x_range'], 
                info['type']
            )
            
            await update.message.reply_photo(
                photo=buf,
                caption=caption,
                parse_mode='HTML',
                reply_markup=get_graph_keyboard()
            )
            
            database.log_message(
                user_id,
                f"graph: {func_str}",
                "graph generated"
            )
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Ошибка при построении графика: {str(e)[:200]}",
                reply_markup=get_graph_keyboard()
            )
    
    async def _draw_graph(self, update: Update, func_str: str):
        """Внутренняя функция построения графика"""
        try:
            result = self.services.plotter.create_graph(func_str)
            
            if result is None:
                await update.message.reply_text("❌ Не удалось построить график")
                return
            
            buf, info = result
            caption = self.formatter.format_graph_info(
                func_str, 
                info['x_range'], 
                info['type']
            )
            
            await update.message.reply_photo(
                photo=buf,
                caption=caption,
                parse_mode='HTML'
            )
            
            database.log_message(
                update.effective_user.id, 
                f"graph: {func_str}", 
                "graph generated"
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)[:200]}")
    
    async def calc_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало режима калькулятора"""
        user_id = update.effective_user.id
        self.bot.user_data[user_id] = {'mode': 'calc', 'expression': ''}
        
        await update.message.reply_text(
            "🔢 <b>Калькулятор</b>\n\n"
            "Введите выражение или используйте кнопки ниже.\n"
            "Нажмите '=' или '🔢 Вычислить' для расчета.\n\n"
            "Для возврата нажмите '⬅️ Назад'.",
            parse_mode='HTML',
            reply_markup=get_calc_keyboard()
        )
    
    async def calc_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /calc"""
        if not context.args:
            await self.calc_start(update, context)
            return
        
        expression = ' '.join(context.args)
        
        try:
            result = self.services.calculator.evaluate(expression)
            response = self.formatter.format_calculation_result(expression, result)
            await update.message.reply_text(response, parse_mode='HTML')
            
            database.log_command(update.effective_user.id, "calc", expression)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")
    
    async def calc_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода в калькуляторе"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id not in self.bot.user_data:
            self.bot.user_data[user_id] = {'mode': 'calc', 'expression': ''}
        
        expression = self.bot.user_data[user_id].get('expression', '')
        
        if text == '⌫' and expression:
            expression = expression[:-1]
        elif text == 'C':
            expression = ''
        elif text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            expression += text
        elif text in ['+', '-', '*', '/', '.', '(', ')', '^']:
            expression += text
        elif text == '√':
            expression += 'sqrt('
        elif text == 'sin':
            expression += 'sin('
        elif text == 'cos':
            expression += 'cos('
        elif text == 'tan':
            expression += 'tan('
        elif text == 'pi':
            expression += 'pi'
        
        self.bot.user_data[user_id]['expression'] = expression
        
        if expression:
            await update.message.reply_text(
                f"📝 Выражение: <code>{expression}</code>",
                parse_mode='HTML',
                reply_markup=get_calc_keyboard()
            )
        else:
            await update.message.reply_text(
                "Введите выражение...",
                reply_markup=get_calc_keyboard()
            )
    
    async def calc_evaluate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Вычисление выражения в калькуляторе"""
        user_id = update.effective_user.id
        
        if user_id not in self.bot.user_data:
            await update.message.reply_text(
                "❌ Сначала запустите калькулятор",
                reply_markup=get_main_keyboard()
            )
            return
        
        expression = self.bot.user_data[user_id].get('expression', '')
        
        if not expression:
            await update.message.reply_text(
                "❌ Выражение пустое",
                reply_markup=get_calc_keyboard()
            )
            return
        
        try:
            result = self.services.calculator.evaluate(expression)
            response = self.formatter.format_calculation_result(expression, result)
            
            await update.message.reply_text(
                response,
                parse_mode='HTML',
                reply_markup=get_calc_keyboard()
            )
            
            database.log_message(
                user_id,
                f"calc: {expression}",
                f"result: {result}"
            )
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Ошибка: {str(e)[:100]}",
                parse_mode='HTML',
                reply_markup=get_calc_keyboard()
            )
    
    async def calc_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Очистка калькулятора"""
        user_id = update.effective_user.id
        if user_id in self.bot.user_data:
            self.bot.user_data[user_id]['expression'] = ''
        
        await update.message.reply_text(
            "🧮 Калькулятор очищен",
            reply_markup=get_calc_keyboard()
        )
    
    async def calc_backspace(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаление последнего символа в калькуляторе"""
        user_id = update.effective_user.id
        
        if user_id in self.bot.user_data:
            expr = self.bot.user_data[user_id].get('expression', '')
            if expr:
                self.bot.user_data[user_id]['expression'] = expr[:-1]
                expr = self.bot.user_data[user_id]['expression']
                
                if expr:
                    await update.message.reply_text(
                        f"📝 Выражение: <code>{expr}</code>",
                        parse_mode='HTML',
                        reply_markup=get_calc_keyboard()
                    )
                else:
                    await update.message.reply_text(
                        "🧮 Выражение очищено",
                        reply_markup=get_calc_keyboard()
                    )
    
    async def about(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        about_text = """
🤖 <b>Math Helper Bot</b>

<b>Версия:</b> 0.0.1
<b>Разработчик:</b> Самарский Илья, Минаев Константин
<b>Описание:</b> Мощный бот-помощник для решения математических задач

<b>Возможности:</b>
• Решение ЛЮБЫХ уравнений
• Построение ЛЮБЫХ графиков
• Интерактивный калькулятор
• Поддержка клавиатурных команд

<b>Используйте кнопки для быстрого доступа к функциям!</b>
"""
        await update.message.reply_text(
            about_text,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        database.log_command(update.effective_user.id, "about")
    
    async def get_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        timezones = {
            'Москва': 'Europe/Moscow',
            'Нью-Йорк': 'America/New_York',
            'Лондон': 'Europe/London',
            'Токио': 'Asia/Tokyo',
            'Пекин': 'Asia/Shanghai',
            'Сидней': 'Australia/Sydney'
        }
        
        time_text = "🕐 <b>Текущее время:</b>\n\n"
        for city, tz in timezones.items():
            now = datetime.now(pytz.timezone(tz))
            time_text += f"• <b>{city}:</b> {now.strftime('%H:%M:%S %d.%m.%Y')}\n"
        
        await update.message.reply_text(
            time_text,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        database.log_command(update.effective_user.id, "time")
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        stats = database.get_stats()
        
        stats_text = f"""
📊 <b>Статистика бота:</b>

👥 <b>Всего пользователей:</b> {stats['total_users']}
💬 <b>Всего сообщений:</b> {stats['total_messages']}
📅 <b>Активных сегодня:</b> {stats['active_today']}

<b>Ваш ID:</b> {user_id}
"""
        await update.message.reply_text(
            stats_text,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        database.log_command(user_id, "stats")
    
    async def hide_keyboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Клавиатура скрыта. Используйте /start для её возврата.",
            reply_markup=ReplyKeyboardRemove()
        )
        database.log_command(update.effective_user.id, "hide_keyboard")
    
    async def back_to_main(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Возврат в главное меню"""
        user_id = update.effective_user.id
        if user_id in self.bot.user_data:
            self.bot.user_data[user_id]['mode'] = 'main'
        
        await update.message.reply_text(
            "<b>Главное меню:</b>\n\nВыберите действие на клавиатуре ниже ⬇️",
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Основной обработчик текстовых сообщений"""
        text = update.message.text
        user_id = update.effective_user.id
        
        if text in self.button_actions:
            await self.button_actions[text](update, context)
            return
        
        if user_id in self.bot.user_data:
            mode = self.bot.user_data[user_id].get('mode', 'main')
            
            if mode == 'solve':
                await self._solve_equation(update, text)
                return
            
            elif mode == 'graph':
                await self.graph_input(update, context)
                return
            
            elif mode == 'calc':
                await self.calc_input(update, context)
                return
        
        if '=' in text and any(c in text for c in 'xX+-*/^'):
            await update.message.reply_text(
                "📝 Похоже, вы ввели уравнение!\n\n"
                "Нажмите '🧮 Решить уравнение' на клавиатуре "
                "или используйте команду /solve для решения.",
                parse_mode='HTML',
                reply_markup=get_main_keyboard()
            )
            return
        
        await update.message.reply_text(
            "Выберите действие на клавиатуре ниже ⬇️",
            reply_markup=get_main_keyboard()
        )