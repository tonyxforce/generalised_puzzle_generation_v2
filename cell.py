from lines import *
from typing import Literal, Any


type Color = Literal["blue"] | Literal["red"]

class Cell():
    """One Square for Urjo"""
    def __init__(self, board, color: Color | None, row_index, column_index, hidden = False, number_hidden = False, number: int | None = None):
        self.color: Color | None = color
        self.hidden: bool = hidden
        self.number: int | None = number
        self.posY: int = column_index
        self.posX: int = row_index
        
        self.row: Any
        self.column: Any
        
        self.board = board
        self.number_hidden: bool = number_hidden

    def get_number(self) -> int | None:
        """Returns the number if the number is visable"""
        if self.number_hidden:
            return None
        return self.number

    def get_color(self) -> Literal["red", "blue"] | None:
        """Returns the color if the number is visable"""
        if self.hidden:
            return None
        return self.color

def invert_color(color: Color | None) -> Literal["red", "blue"] | None:
    """Returns the opposite color as a string"""
    if color == "blue":
        return "red"
    if color == "red":
        return "blue"
    if color == None:
        return None
    raise Exception(f"Invalid color '{color}' provided!")