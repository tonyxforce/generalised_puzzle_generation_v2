import random
from collections import deque

from typing import List

from lines import *
from square import *


class UrjoBoard():
    """The Urjo puzzle, made up of rows and columns"""

    def __init__(self, rows: List[UrjoRow] = [], columns: list[UrjoColumn] = []):
        self.rows = rows
        self.columns = columns
        self.numbered_slots = []
        self.all_numbers: List[UrjoSquare] = []
        # Technically you could just use all_numbers and not double store this but it makes it easier to read and comprehend imo
        self.all_squares: List[UrjoSquare] = []
        self.contradiction_count = 0
        self.removed_by_identical = 0

    def __str__(self):
        """how a puzzle prints out, for testing purposes"""
        lines = []
        for row in self.rows:
            line = []
            for square in row.row:
                if square.color == "blue":
                    line.append("b")
                elif square.color == "red":
                    line.append("r")
                elif square.get_color() is None:
                    line.append(".")
                else:
                    line.append("?")
            lines.append(" ".join(line))
        return "\n".join(lines)

    @classmethod
    def from_url(self, url_str: str, dim1: int, dim2: int):
        """converts a url into a urjo puzzle"""
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if len(url_str) != dim1 * dim2:
            raise ValueError("URL length does not match provided dimensions")

        board = self()
        board.rows = [UrjoRow([]) for _ in range(dim2)]
        board.columns = [UrjoColumn([]) for _ in range(dim1)]
        board.all_squares = []
        board.all_numbers = []

        for y in range(dim2):
            for x in range(dim1):
                new_square = UrjoSquare(board, None, y, x)
                new_square.row = board.rows[y]
                new_square.column = board.columns[x]
                board.rows[y].row.append(new_square)
                board.columns[x].column.append(new_square)
                board.all_squares.append(new_square)

        for idx, ch in enumerate(url_str):
            value = alphabet.index(ch)
            visible_bit = value & 1
            color_bit = (value >> 1) & 1
            num_val = value >> 2

            sq = board.all_squares[idx]

            sq.color = "blue" if color_bit == 0 else "red"

            sq.hidden = (visible_bit == 0)

            if num_val > 0:
                sq.number = num_val - 1
                sq.number_hidden = False
            else:
                sq.number = None
                sq.number_hidden = True

        for row in board.rows:
            row.set_allowed_size()
        for col in board.columns:
            col.set_allowed_size()

        board.all_numbers = [
            sq for sq in board.all_squares if sq.number is not None]

        return board

    def snapshot_state(self):
        """Stores the current board to revert to later"""
        snap: list[tuple[UrjoSquare, Literal["red", "blue"], bool]] = []
        for row in self.rows:
            for sq in row.get_squares():
                snap.append((sq, sq.color, sq.hidden))
        return snap

    def restore_state(self, snapshot: list[tuple[UrjoSquare, Literal["red", "blue"], bool]]):
        """Reverts to the saved board"""
        for sq, col, hidden in snapshot:
            sq.color = col
            sq.hidden = hidden

    def hide_numbers(self, remaining_numbers):
        """Hides all but remaining_numbers numbers"""
        random.shuffle(self.all_numbers)
        for i, number in enumerate(self.all_numbers):
            if i < remaining_numbers:
                pass
            else:
                number.number_hidden = True

    def get_surrounding_slots(self, square: UrjoSquare):
        """Returns the surrounding slots around a square"""
        r = square.row_index
        c = square.column_index
        rows = len(self.rows)
        cols = len(self.columns)

        def at(rr: int, cc: int):
            # return the cell at (rr,cc) if it exists, otherwise None.
            if 0 <= rr < rows and 0 <= cc < cols:
                row_list = self.rows[rr].get_squares()
                if 0 <= cc < len(row_list):
                    return row_list[cc]
            return None

        up_left = at(r - 1, c - 1)
        up = at(r - 1, c)
        up_right = at(r - 1, c + 1)
        left = at(r, c - 1)
        right = at(r, c + 1)
        down_left = at(r + 1, c - 1)
        down = at(r + 1, c)
        down_right = at(r + 1, c + 1)

        return up_left, up, up_right, left, right, down_left, down, down_right

    def get_number(self, slot: UrjoSquare):
        """Gets the number for a slot, doesnt work if not all slots are colored"""
        surrounding_slots = self.get_surrounding_slots(slot)
        color = slot.color
        total = 0
        for square in surrounding_slots:
            if square is not None:
                if square.color == color:
                    total += 1
        slot.number = total

    def fill_numbers(self):
        """Puts all numbers on the full board"""
        for row in self.rows:
            for square in row.row:
                self.get_number(square)

    def to_url_format(self):
        """Sends the current puzzle into a url format"""
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        chars = []

        for row in self.rows:
            for sq in row.get_squares():
                if sq.number is not None and not sq.number_hidden:
                    num_val = sq.number + 1
                else:
                    num_val = 0

                if num_val > 15 or num_val < 0:
                    # Never encountered in real world scenarios
                    raise ValueError(f"Invalid number {num_val} received")

                color_bit = 0 if sq.color == "blue" else 1

                visible_bit = 0 if sq.hidden else 1

                value = (num_val << 2) | (color_bit << 1) | visible_bit

                chars.append(alphabet[value])

        return "".join(chars)

    def fill_row(self, row):
        """Fills a row if it can be filled with a color"""
        return self.__fill__(row, math.ceil(len(row.row)/2))

    def fill_column(self, column):
        """Fills a column if it can be filled with a color"""
        return self.__fill__(column, math.ceil(len(column.column)/2))

    def __fill__(self, obj: UrjoRow | UrjoColumn, max):
        """Fills an object will required remaining colors if possible, else does nothing"""
        red, blue, uncolored = obj.count_colors()
        squares = []
        if red == max:
            for square in obj.get_squares():
                if square.get_color() is None:  # uses get_color(), so only visiable colors are counted, be careful
                    square.color = "blue"
                    square.hidden = False
                    squares.append(square)

            return True, squares

        if blue == max:
            for square in obj.get_squares():
                if square.get_color() is None:  # uses get_color(), so only visiable colors are counted, be careful
                    square.color = "red"
                    square.hidden = False
                    squares.append(square)

            return True, squares

        return False, []

    def unfill(self, integer):
        """Duplicate function for unfilling numbers, dont know why I made two, this code has gotten so long im not noticing a lot"""
        random.shuffle(self.all_numbers)

        for i, sq in enumerate(self.all_numbers):
            if i < integer:
                sq.number_hidden = False
            else:
                sq.number_hidden = True

def fill_single_number(slot: UrjoSquare):
    """
    Fills the number cell and/or its surrounding slots and returns a tuple(bool, list)
    indicating whether it has changed anything and if it has, what
    """

    if slot is None:
        raise ValueError("Invalid slot received")

    target = slot.get_number()
    if target is None:
        return False, []

    board = slot.board
    surrounding_all = board.get_surrounding_slots(slot)
    surrounding = [s for s in surrounding_all if s is not None]
    total = len(surrounding)

    # Should use get_color_counts instead
    red = blue = uncol = 0
    for slt in surrounding:
        color = slt.get_color()
        if color == "red":
            red += 1
        elif color == "blue":
            blue += 1
        else:
            uncol += 1

    # Just double checking the target isnt something stupid like 13 or lower then 0 which can technically be encoded
    if target < 0 or target > total:
        return False, []

    required_same = target
    required_opp = total - target

    changed = False
    filled_slots = []

    # possibly determine the number cell's color
    def feasible_if_color(color):
        if color == "red":
            same_count, opp_count = red, blue
        else:
            same_count, opp_count = blue, red
        if same_count > required_same or same_count + uncol < required_same:
            return False
        if opp_count > required_opp or opp_count + uncol < required_opp:
            return False
        return True

    num_color = slot.get_color()
    if num_color is None:
        can_red = feasible_if_color("red")
        can_blue = feasible_if_color("blue")
        if can_red != can_blue:
            slot.color = "red" if can_red else "blue"
            slot.hidden = False
            changed = True
            filled_slots.append(slot)
            num_color = slot.color
        elif not (can_red or can_blue):
            return False, []

    if num_color is None:
        return changed, filled_slots

    # forced fills among surrounding slots due to number

    if num_color == "red":
        same, opp = red, blue
        same_col, opp_col = "red", "blue"
    else:
        same, opp = blue, red
        same_col, opp_col = "blue", "red"

    # same meets target (unassigned must be opposite)
    if same == required_same and uncol > 0:
        for s in surrounding:
            if s.get_color() is None:
                s.color = opp_col
                s.hidden = False
                changed = True
                filled_slots.append(s)
        return changed, filled_slots

    # opposite meets target (unassigned must be same)
    if opp == required_opp and uncol > 0:
        for s in surrounding:
            if s.get_color() is None:
                s.color = same_col
                s.hidden = False
                changed = True
                filled_slots.append(s)
        return changed, filled_slots

    # same + uncol == required_same (all unassigned required to be the same)
    if same + uncol == required_same and uncol > 0:
        for s in surrounding:
            if s.get_color() is None:
                s.color = same_col
                s.hidden = False
                changed = True
                filled_slots.append(s)
        return changed, filled_slots

    # opposite + uncol == required_opp (all unassigned opposite color)
    if opp + uncol == required_opp and uncol > 0:
        for s in surrounding:
            if s.get_color() is None:
                s.color = opp_col
                changed = True
                filled_slots.append(s)
        return changed, filled_slots

    # Can't fill any slots
    return changed, filled_slots
