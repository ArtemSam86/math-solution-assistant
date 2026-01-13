from graph_plotter import GraphPlotter
from calculator import Calculator
from equation_solver import EquationSolver

class Services:
    """Контейнер сервисов бота"""
    def __init__(self):
        self.plotter = GraphPlotter()
        self.calculator = Calculator()
        self.solver = EquationSolver()