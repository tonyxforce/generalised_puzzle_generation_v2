class UrjoSquare():
    """One Square for Urjo"""
    def __init__(self, board, color, row_index, column_index, row=None, column=None, hidden_bool = False, number_hidden = False, number = None):
        self.color = color
        self.row = row
        self.column = column
        self.hidden_bool = hidden_bool
        self.number = number
        self.column_index = column_index
        self.row_index = row_index
        self.board = board
        self.number_hidden = number_hidden

    def get_number(self):
        """Returns the number if the number is visable"""
        if self.number_hidden:
            return None
        return self.number

    def get_color(self):
        """Returns the color if the number is visable"""
        if self.hidden_bool:
            return None
        return self.color

def invert_color(color):
    """Returns the opposite color"""
    if color == "blue":
        return "red"
    if color == "red":
        return "blue"
    raise Exception(f"Invalid color '{color}' provided!")
