import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import re
from typing import Tuple, Optional, Dict, Any
import warnings

warnings.filterwarnings("ignore")

class GraphPlotter:
    def __init__(self):
        self.standard_functions = {
            'x^2': lambda x: x**2,
            'x**2': lambda x: x**2,
            'sin(x)': lambda x: np.sin(x),
            'cos(x)': lambda x: np.cos(x),
            'tan(x)': lambda x: np.tan(x),
            'exp(x)': lambda x: np.exp(x),
            'e^x': lambda x: np.exp(x),
            'ln(x)': lambda x: np.log(x),
            'log(x)': lambda x: np.log(x),
            'sqrt(x)': lambda x: np.sqrt(x),
            '√(x)': lambda x: np.sqrt(x),
            '1/x': lambda x: 1/x,
            '|x|': lambda x: np.abs(x),
            'abs(x)': lambda x: np.abs(x),
            'x^3': lambda x: x**3,
            'x**3': lambda x: x**3,
        }
    
    def _safe_eval(self, expr: str, x: float) -> Optional[float]:
        """Безопасное вычисление выражения для одного значения x"""
        try:
            expr = expr.replace('^', '**')
            expr = expr.replace('√', 'np.sqrt')
            expr = expr.replace('abs', 'np.abs')
            expr = expr.replace('ln', 'np.log')
            expr = expr.replace('log', 'np.log10')
            expr = expr.replace('e^', 'np.exp')
            expr = expr.replace('exp', 'np.exp')
            expr = expr.replace('sin', 'np.sin')
            expr = expr.replace('cos', 'np.cos')
            expr = expr.replace('tan', 'np.tan')
            
            if '1/x' in expr or '/x' in expr:
                if abs(x) < 0.001:
                    return None
            
            result = eval(expr, {
                'x': x,
                'np': np,
                'pi': np.pi,
                'e': np.e,
                'sqrt': np.sqrt,
                'exp': np.exp,
                'log': np.log,
                'log10': np.log10,
                'sin': np.sin,
                'cos': np.cos,
                'tan': np.tan,
                'abs': np.abs
            })
            
            if np.isnan(result) or np.isinf(result):
                return None
            
            return float(result)
            
        except (ZeroDivisionError, ValueError, TypeError, SyntaxError):
            return None
    
    def _get_x_range(self, func_str: str) -> Tuple[float, float]:
        """Определяет подходящий диапазон для x"""
        func_lower = func_str.lower()
        
        if 'exp' in func_lower or 'e^' in func_lower:
            return (-3, 3)
        
        if 'ln' in func_lower or 'log(' in func_lower:
            return (0.1, 5)
        
        if '1/x' in func_lower or '/x' in func_lower:
            return (-5, 5)
        
        return (-5, 5)
    
    def _detect_discontinuities(self, func_str: str, x_range: Tuple[float, float]) -> list:
        """Обнаруживает точки разрыва"""
        func_lower = func_str.lower()
        discontinuities = []
        
        if '1/x' in func_lower or '/x' in func_lower:
            if x_range[0] < 0 < x_range[1]:
                discontinuities.append(0)
        
        if 'tan(' in func_lower:
            n_min = int(np.ceil((x_range[0] - np.pi/2) / np.pi))
            n_max = int(np.floor((x_range[1] - np.pi/2) / np.pi))
            for n in range(n_min, n_max + 1):
                point = np.pi/2 + n * np.pi
                if x_range[0] < point < x_range[1]:
                    discontinuities.append(point)
        
        return discontinuities
    
    def create_graph(self, func_str: str) -> Optional[Tuple[io.BytesIO, Dict[str, Any]]]:
        """Создает график функции и возвращает его в буфере"""
        try:
            x_min, x_max = self._get_x_range(func_str)
            
            discontinuities = self._detect_discontinuities(func_str, (x_min, x_max))
            
            segments = []
            points = sorted([x_min] + discontinuities + [x_max])
            
            for i in range(len(points) - 1):
                seg_start, seg_end = points[i], points[i + 1]
                
                if seg_end - seg_start < 0.01:
                    continue
                
                seg_x = np.linspace(seg_start, seg_end, 400)
                seg_y = []
                valid_x = []
                
                for x_val in seg_x:
                    y_val = self._safe_eval(func_str, x_val)
                    if y_val is not None:
                        if ('1/x' in func_str.lower() or '/x' in func_str.lower()) and abs(x_val) < 0.1:
                            if abs(y_val) > 50:
                                continue
                        
                        seg_y.append(y_val)
                        valid_x.append(x_val)
                
                if len(valid_x) >= 2:
                    segments.append((np.array(valid_x), np.array(seg_y)))
            
            if not segments:
                print(f"Не удалось построить график для функции: {func_str}")
                return None
            
            plt.figure(figsize=(10, 6), dpi=100)
            
            graph_type = "continuous"
            if discontinuities:
                graph_type = "discontinuous"
                
                for disc_point in discontinuities:
                    plt.axvline(x=disc_point, color='red', linestyle='--', alpha=0.5, linewidth=1)
            
            for seg_x, seg_y in segments:
                plt.plot(seg_x, seg_y, linewidth=2, color='blue', alpha=0.7)
            
            if '1/x' in func_str.lower() or '/x' in func_str.lower():
                plt.axhline(y=0, color='green', linestyle='--', alpha=0.5, linewidth=1)
            
            plt.title(f'График функции: {func_str}', fontsize=14, pad=20)
            plt.xlabel('x', fontsize=12)
            plt.ylabel('f(x)', fontsize=12)
            plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            plt.axhline(y=0, color='black', linewidth=0.8)
            plt.axvline(x=0, color='black', linewidth=0.8)
            
            all_y = []
            for _, seg_y in segments:
                all_y.extend(seg_y)
            
            if all_y:
                y_min, y_max = min(all_y), max(all_y)
                y_range = y_max - y_min
                
                if y_range > 100 and ('exp' in func_str.lower() or 'e^' in func_str.lower()):
                    plt.yscale('log')
                    plt.ylabel('f(x) (log scale)', fontsize=12)
                else:
                    if y_range < 0.1:
                        y_margin = 0.5
                    elif y_range < 10:
                        y_margin = y_range * 0.2
                    else:
                        y_margin = y_range * 0.1
                    
                    plt.ylim(y_min - y_margin, y_max + y_margin)
            
            x_range = x_max - x_min
            plt.xlim(x_min - x_range * 0.05, x_max + x_range * 0.05)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, 
                       facecolor='white', edgecolor='none')
            buf.seek(0)
            plt.close()
            
            info = {
                'x_range': (x_min, x_max),
                'type': graph_type,
                'function': func_str,
                'segments': len(segments)
            }
            
            print(f"График для функции '{func_str}' успешно построен")
            return buf, info
            
        except Exception as e:
            print(f"Ошибка при построении графика для '{func_str}': {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def quick_test(self):
        """Быстрый тест функций"""
        test_functions = ['exp(x)', '1/x', 'x^2', 'sin(x)', 'ln(x)']
        
        for func in test_functions:
            print(f"\nТестируем функцию: {func}")
            result = self.create_graph(func)
            if result:
                print(f"✓ График построен успешно")
            else:
                print(f"✗ Ошибка построения")