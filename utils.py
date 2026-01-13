import re
import math
from typing import Optional, Dict, Any


def validate_equation(equation: str) -> bool:
    if '=' not in equation:
        return False

    safe_pattern = r'^[0-9xX\+\-\*\/\^\(\)\=\s\.a-zA-Z_,!@#\$%\^&\*\?<>\[\]\{\}\|\~`]+$'
    return bool(re.match(safe_pattern, equation))


def clean_input(text: str) -> str:
    return ' '.join(text.strip().split())


def format_number(num: float, precision: int = 6) -> str:
    if isinstance(num, complex):
        real = format_number(num.real, precision)
        imag = format_number(num.imag, precision)
        if num.imag >= 0:
            return f"{real}+{imag}i"
        else:
            return f"{real}{imag}i"
    
    if num.is_integer():
        return str(int(num))
    
    formatted = f"{num:.{precision}f}"
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')
    return formatted


def escape_markdown(text: str) -> str:
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def preprocess_equation_extended(equation: str) -> str:
    original = equation
    
    equation = equation.replace('^', '**')
    equation = equation.replace('ln', 'log')
    equation = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation)
    equation = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', equation)
    equation = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', equation)
    equation = re.sub(r'(\))([a-zA-Z\d])', r'\1*\2', equation)
    equation = re.sub(r'(\d)(\()', r'\1*\2', equation)
    
    function_replacements = {
        'sin': 'sympy.sin',
        'cos': 'sympy.cos', 
        'tan': 'sympy.tan',
        'cot': 'sympy.cot',
        'sec': 'sympy.sec',
        'csc': 'sympy.csc',
        'asin': 'sympy.asin',
        'acos': 'sympy.acos',
        'atan': 'sympy.atan',
        'sinh': 'sympy.sinh',
        'cosh': 'sympy.cosh',
        'tanh': 'sympy.tanh',
        'sqrt': 'sympy.sqrt',
        'exp': 'sympy.exp',
        'log': 'sympy.log',
        'ln': 'sympy.log',
        'abs': 'sympy.Abs',
        'floor': 'sympy.floor',
        'ceil': 'sympy.ceil'
    }
    
    for old, new in function_replacements.items():
        equation = re.sub(rf'\b{old}\b', new, equation)
    
    equation = re.sub(r'\be\b', 'sympy.E', equation)
    equation = re.sub(r'\bpi\b', 'sympy.pi', equation)
    equation = re.sub(r'\|([^|]+)\|', r'sympy.Abs(\1)', equation)
    
    return equation


def prepare_equation_for_display(equation: str) -> str:
    replacements = {
        '**': '²',
        '^': '²',
        '*': '×',
        '/': '÷',
        'sqrt': '√',
        'pi': 'π',
        'exp': 'e^',
        'log': 'ln',
        'sympy.': ''
    }
    
    for old, new in replacements.items():
        equation = equation.replace(old, new)
    
    return equation


def get_function_properties(func_str: str) -> Dict[str, Any]:
    properties = {
        'type': 'unknown',
        'degree': None,
        'periodic': False,
        'symmetric': False,
        'domain': 'ℝ',
        'range': 'ℝ'
    }
    
    func_lower = func_str.lower()
    
    if any(trig in func_lower for trig in ['sin', 'cos', 'tan', 'cot', 'sec', 'csc']):
        properties['type'] = 'trigonometric'
        properties['periodic'] = True
    elif 'exp' in func_lower or 'e^' in func_lower:
        properties['type'] = 'exponential'
        properties['range'] = '(0, ∞)'
    elif 'log' in func_lower or 'ln' in func_lower:
        properties['type'] = 'logarithmic'
        properties['domain'] = '(0, ∞)'
    elif 'sqrt' in func_lower:
        properties['type'] = 'radical'
        properties['domain'] = '[0, ∞)'
        properties['range'] = '[0, ∞)'
    elif any(op in func_lower for op in ['^', '**']):
        properties['type'] = 'polynomial'
        match = re.search(r'\^(\d+)|\*\*(\d+)', func_lower)
        if match:
            properties['degree'] = int(match.group(1) or match.group(2))
    
    if 'x^2' in func_lower or 'x**2' in func_lower:
        properties['symmetric'] = True
    
    return properties