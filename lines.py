import math

from typing import List, Literal

from cell import Cell

class Line:
    """Row and Columns are at their heart the same thing, so both direct into this parent class which does all the calculations"""
    attribute_name = None   # overrided in subclasses to be either .row or .column
    cells: List[Cell] = []

    def __init__(self, value):
        cells = []
        self.color_count = 0
        self.cells: List[Cell] = []

    def _cmp_key(self):
        """
        Lowkey a mess of a method honestly, just ignore it
        """
        colors: List[Literal["red", "blue"]] = []
        for cell in self.cells:
            color = cell.get_color()
            if color is None:
                return None
            colors.append(color)

        red_count = colors.count("red")
        blue_count = colors.count("blue")

        if self.color_count is not None and red_count == self.color_count:
            return tuple(i for i, c in enumerate(colors) if c == "red")

        if self.color_count is not None and blue_count == self.color_count:
            return tuple(i for i, c in enumerate(colors) if c == "blue")

        return tuple(colors)

    def __eq__(self, other):
        """Also doesnt really work but we shall ignore it because it isnt used for generation currently LOL"""
        if not isinstance(other, Line):
            return NotImplemented
        cmp_key = self._cmp_key()
        other_cmp_key = other._cmp_key()
        if cmp_key is None or other_cmp_key is None:
            return False
        return cmp_key == other_cmp_key


    def set_allowed_size(self):
        # sets the maximum of a color in the row
        self.color_count: int = math.ceil(len(self.get_cells()) / 2)

    def check_color_count(self):
        """makes sure there are maximum of allowed_size colors in a row"""
        red, blue, uncolored = self.count_colors()
        if blue > self.color_count:
            return False
        elif red > self.color_count:
            return False
        return True

    def get_cells(self) -> List[Cell]:
        # """gets all squares in the row/column"""
        return self.cells

    def count_colors(self):
        """Gets the color count of the row, kinda depricated because you can use get_color_counts(row.row) or get_color_counts(column.column)"""
        red = 0
        blue = 0
        uncolored = 0
        # iterate the actual square objects
        for square in self.get_cells():
            if square.get_color() == "blue":
                blue += 1
            elif square.get_color() == "red":
                red += 1
            else:
                uncolored += 1
        return red, blue, uncolored

class UrjoRow(Line):
    """row object inheriting directly from the rowcolumn parent"""
    attribute_name = "row"
    def __init__(self, value):
        setattr(self, self.attribute_name, value)
        self.allowed_size = None
        self.cells = value

class UrjoColumn(Line):
    """column object inheriting directly from the rowcolumn parent"""
    attribute_name = "column"
    def __init__(self, value):
        setattr(self, self.attribute_name, value)
        self.allowed_size = None
        self.cells = value

def get_color_counts(slots: List[Cell | None]):
    """counts each color in the provided slots"""
    red = 0
    blue = 0
    uncolored = 0
    for slot in slots:
        if slot is not None:
            if slot.get_color() == "red":
                red +=1
            if slot.get_color() == "blue":
                blue +=1
            if slot.get_color() == None:
                uncolored +=1
    return red, blue, uncolored

def nonIdentical(lst, index):
    """checks if the lines around it are identical"""
    if index > 0:
        if lst[index-1] == lst[index]:
            return False
    if index < (len(lst)-1):
        if lst[index + 1] == lst[index]:
            return False
    return True

def lines_different(line_1: UrjoRow | UrjoColumn, line_2: UrjoRow | UrjoColumn):
    """returns False if two lines are the same, to be honest dont trust this due to eq and cmp_key not really working"""
    for i, sq in enumerate(line_1.get_cells()):
        if sq.get_color() != line_2.get_cells()[i].get_color():
            return True
    return False

def check_row_and_column(cell: Cell):
    """checks the row and column for a slot"""
    if cell.row is None or cell.column is None:
        raise Exception("Cannot use check_row_and_column on a sole cell!")
    if cell.row.check_color_count() and cell.column.check_color_count():
        return True
    return False