from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    """Главная клавиатура"""
    keyboard = [
        ['🧮 Решить уравнение', '📊 Построить график'],
        ['🔢 Калькулятор', '🕐 Текущее время'],
        ['📚 Помощь', 'ℹ️ О боте'],
        ['📊 Статистика', '❌ Скрыть клавиатуру']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_calc_keyboard():
    """Клавиатура калькулятора"""
    keyboard = [
        ['7', '8', '9', '/', 'C'],
        ['4', '5', '6', '*', '⌫'],
        ['1', '2', '3', '-', 'sin'],
        ['0', '.', '=', '+', 'cos'],
        ['√', '(', ')', '^', 'tan'],
        ['pi', '⬅️ Назад', '🔢 Вычислить']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_graph_keyboard():
    """Клавиатура графика"""
    keyboard = [
        ['x^2', 'sin(x)', 'cos(x)', 'e^x'],
        ['ln(x)', '√(x)', '1/x', '|x|'],
        ['x^3', '📈 Построить', '⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)