import sympy
import numpy as np
import logging
from typing import List, Tuple, Dict, Any
import utils

logger = logging.getLogger(__name__)


class EquationSolver:
    def __init__(self):
        pass

    def solve(self, equation: str) -> Dict[str, Any]:
        result = {
            'solutions': [],
            'equation': equation,
            'type': 'unknown',
            'error': False,
            'error_message': '',
            'count': 0
        }

        try:
            if '=' not in equation:
                result['error'] = True
                result['error_message'] = "❌ Уравнение должно содержать '='"
                return result

            x = sympy.symbols('x')
            equation = equation.replace('^', '**')
            
            try:
                left, right = equation.split('=', 1)
                expr = sympy.sympify(f"({left.strip()}) - ({right.strip()})")
                solutions = sympy.solve(expr, x)
            except Exception as e:
                result['error'] = True
                result['error_message'] = f"❌ Не удалось решить уравнение: {str(e)[:100]}"
                return result

            if not solutions:
                result['error'] = True
                result['error_message'] = "❌ Уравнение не имеет решений"
                return result

            result['solutions'] = solutions
            result['count'] = len(solutions)
            result['type'] = self._determine_equation_type(equation, solutions)
            
        except Exception as e:
            logger.error(f"Equation solving error: {e}")
            result['error'] = True
            result['error_message'] = f"❌ Ошибка: {str(e)[:200]}"

        return result

    def _determine_equation_type(self, equation: str, solutions) -> str:
        equation_lower = equation.lower()
        
        if any('sin' in equation_lower or 'cos' in equation_lower or 'tan' in equation_lower for _ in solutions):
            return 'тригонометрическое'
        elif 'exp' in equation_lower:
            return 'экспоненциальное'
        elif 'log' in equation_lower or 'ln' in equation_lower:
            return 'логарифмическое'
        elif len(solutions) > 2:
            return f'полиномиальное {len(solutions)}-й степени'
        elif len(solutions) == 2:
            return 'квадратное'
        elif len(solutions) == 1:
            return 'линейное'
        
        return 'алгебраическое'

    def format_solution(self, result: Dict[str, Any]) -> str:
        if result['error']:
            return result['error_message']

        equation = result['equation']
        solutions = result['solutions']
        eq_type = result['type']

        display_eq = self._format_equation(equation)

        response = f"🧮 Уравнение: {display_eq}\n\n"

        if len(solutions) == 1:
            response += "✅ Решение найдено:\n\n"
        else:
            response += f"✅ Найдено {len(solutions)} решений:\n\n"

        for i, sol in enumerate(solutions, 1):
            sol_str = self._format_solution_value(sol)
            response += f"{i}. x = {sol_str}\n"

        response += f"\n📝 Тип: {eq_type}"
        
        complex_solutions = [sol for sol in solutions if self._is_complex_number(sol)]
        if complex_solutions:
            response += "\n\n💡 *i* обозначает мнимую единицу (√-1)"

        return response

    def _format_equation(self, equation: str) -> str:
        """Форматирует уравнение для отображения"""
        eq = equation.replace('**2', '²').replace('**3', '³')
        eq = eq.replace('*', '×').replace('/', '÷')
        eq = eq.replace('sqrt', '√').replace('pi', 'π')
        eq = eq.replace('exp', 'e^').replace('log', 'ln')
        return eq

    def _format_solution_value(self, solution) -> str:
        """Форматирует значение решения"""
        try:
            sol_str = str(solution)
            
            replacements = [
                ('I', 'i'),
                ('sqrt', '√'),
                ('**', '^'),
                ('*', ''),
                ('(', ''),
                (')', ''),
                (' ', '')
            ]
            
            for old, new in replacements:
                sol_str = sol_str.replace(old, new)
            
            if 'i' in sol_str:
                if sol_str.startswith('-') and sol_str[1:].startswith('-'):
                    sol_str = sol_str.replace('--', '+')
            
            return sol_str
        except:
            return str(solution)

    def _is_complex_number(self, solution) -> bool:
        """Проверяет, является ли число комплексным"""
        try:
            sol_str = str(solution)
            return 'I' in sol_str or 'sqrt' in sol_str
        except:
            return False

    def _find_numerical_solutions(self, equation_sympy, x, ranges: List[Tuple[float, float]] = None) -> List[float]:
        if ranges is None:
            ranges = [(-10, 10), (-100, 100), (-1000, 1000)]
        
        solutions = []
        
        for start, end in ranges:
            for guess in np.linspace(start, end, 10):
                try:
                    sol = sympy.nsolve(equation_sympy, x, guess, tol=1e-10, maxsteps=100)
                    
                    if sol is not None:
                        sol_float = float(sol)
                        if not any(abs(sol_float - existing) < 1e-6 for existing in solutions):
                            solutions.append(sol_float)
                            
                except (ValueError, ZeroDivisionError, RuntimeError):
                    continue
                    
        return solutions