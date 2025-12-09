from lines import *
from typing import Literal

class UrjoSquare():
    """One Square for Urjo"""
    def __init__(self, board, color: Literal["red", "blue", None], row_index, column_index, row=None, column=None, hidden_bool = False, number_hidden = False, number = None):
        self.color: Literal["red", "blue", None] = color
        self.row: UrjoRow = row
        self.column: UrjoColumn = column
        self.hidden: bool = hidden_bool
        self.number: int = number
        self.column_index: int = column_index
        self.row_index: int = row_index
        self.board = board
        self.number_hidden: bool = number_hidden

    def get_number(self) -> int:
        """Returns the number if the number is visable"""
        if self.number_hidden:
            return None
        return self.number

    def get_color(self) -> bool:
        """Returns the color if the number is visable"""
        if self.hidden:
            return None
        return self.color

def invert_color(color) -> Literal["red", "blue"]:
    """Returns the opposite color as a string"""
    if color == "blue":
        return "red"
    if color == "red":
        return "blue"
    raise Exception(f"Invalid color '{color}' provided!")