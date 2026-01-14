import re
import math
from typing import Union, List

class Calculator:
    def __init__(self):
        self.operations = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else float('inf'),
            '^': lambda a, b: a ** b,
            '**': lambda a, b: a ** b,
        }
        
        self.functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'log': math.log10,
            'ln': math.log,
            'exp': math.exp,
            'abs': abs,
        }
    
    def evaluate(self, expression: str) -> Union[float, str]:
        """Основной метод вычисления выражения"""
        try:
            expression = expression.replace(' ', '').replace('^', '**')
            
            expression = expression.replace('√', 'sqrt')
            expression = expression.replace('pi', str(math.pi))
            expression = expression.replace('π', str(math.pi))
            expression = expression.replace('e', str(math.e))
            dangerous_patterns = ['__', 'import', 'exec', 'eval', 'open', 'file', 'os.', 'sys.', 'subprocess']
            expr_lower = expression.lower()
            for pattern in dangerous_patterns:
                if pattern in expr_lower:
                    raise ValueError("Выражение содержит недопустимые команды")
            
            for func_name in ['sin', 'cos', 'tan', 'sqrt', 'log', 'ln', 'exp', 'abs']:
                if func_name in expr_lower:
                    expression = re.sub(
                        fr'{func_name}\((.+?)\)',
                        lambda m: f'math.{func_name}({m.group(1)})',
                        expression
                    )
            
            allowed_names = {
                'math': math,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'sqrt': math.sqrt,
                'log': math.log10,
                'ln': math.log,
                'exp': math.exp,
                'abs': abs,
                'pi': math.pi,
                'e': math.e
            }
            
            if any(word in expression.lower() for word in ['import', '__', 'exec', 'eval', 'open', 'file']):
                raise ValueError("Выражение содержит недопустимые команды")
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            if result == float('inf') or result == float('-inf'):
                return "∞" if result > 0 else "-∞"
            
            if math.isnan(result):
                return "Не определено"
            
            if abs(result - round(result)) < 1e-10:
                return int(round(result))
            
            return round(result, 10)
            
        except ZeroDivisionError:
            raise ValueError("Деление на ноль")
        except SyntaxError:
            raise ValueError("Синтаксическая ошибка в выражении")
        except NameError as e:
            raise ValueError(f"Неизвестная функция или переменная: {str(e)}")
        except Exception as e:
            raise ValueError(f"Неправильное выражение: {str(e)}")