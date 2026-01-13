class MessageFormatter:
    def __init__(self):
        pass
    
    def format_equation_solution(self, result: dict) -> str:
        """Форматирует решение уравнения"""
        if result['error']:
            return result['error_message']
        
        solutions = result.get('solutions', [])
        equation = result.get('equation', '')
        count = result.get('count', 0)
        
        if count == 0:
            return f"📌 Уравнение: <b>{equation}</b>\n\n❌ Уравнение не имеет решений"
        
        elif count == 1:
            sol = solutions[0]
            if isinstance(sol, (int, float)):
                sol_str = f"<b>{sol:.6f}</b>"
                if abs(sol - round(sol)) < 1e-10:
                    sol_str = f"<b>{int(round(sol))}</b>"
            else:
                sol_str = f"<b>{sol}</b>"
            
            return f"📌 Уравнение: <b>{equation}</b>\n\n✅ Найдено решение:\n\nx = {sol_str}"
        
        else:
            solutions_text = []
            for i, sol in enumerate(solutions, 1):
                if isinstance(sol, (int, float)):
                    sol_str = f"{sol:.6f}"
                    if abs(sol - round(sol)) < 1e-10:
                        sol_str = f"{int(round(sol))}"
                else:
                    sol_str = str(sol)
                
                solutions_text.append(f"x{i} = <b>{sol_str}</b>")
            
            solutions_block = "\n".join(solutions_text)
            
            return f"📌 Уравнение: <b>{equation}</b>\n\n✅ Найдено решений: <b>{count}</b>\n\n{solutions_block}"
    
    def format_calculation_result(self, expression: str, result) -> str:
        """Форматирует результат вычисления"""
        if isinstance(result, str):
            result_str = result
        elif isinstance(result, (int, float)):
            if result == int(result):
                result_str = str(int(result))
            else:
                result_str = f"{result:.10f}".rstrip('0').rstrip('.')
        else:
            result_str = str(result)
        
        return f"🧮 Выражение: <code>{expression}</code>\n\n✅ Результат: <b>{result_str}</b>"
    
    def format_graph_info(self, func_str: str, x_range: tuple, graph_type: str) -> str:
        """Форматирует информацию о графике"""
        range_text = f"от {x_range[0]} до {x_range[1]}"
        
        if graph_type == "discontinuous":
            type_text = "Разрывная функция"
        else:
            type_text = "Непрерывная функция"
        
        return f"📊 График функции:\n<b>{func_str}</b>\n\n📏 Диапазон x: {range_text}\n📋 Тип: {type_text}"
    
    def format_error_message(self, error: str, context: str = "") -> str:
        """Форматирует сообщение об ошибке"""
        if context:
            return f"❌ Ошибка в {context}:\n{error}"
        return f"❌ Ошибка:\n{error}"