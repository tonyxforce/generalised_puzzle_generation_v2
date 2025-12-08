import math
import random
from collections import deque
class UrjoSquare():
    """One Square for Urjo"""
    def __init__(self, board, colour, row_index, column_index, row=None, column=None, hidden_bool = False, number_hidden = False, number = None):
        self.colour = colour
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

    def get_colour(self):
        """Returns the colour if the number is visable"""
        if self.hidden_bool:
            return None
        return self.colour

class RowColumnParent:
    """Row and Columns are at their heart the same thing, so both direct into this parent class which does all the calculations"""
    attribute_name = None   # overrided in subclasses to be either .row or .column

    def __init__(self, value):
        setattr(self, self.attribute_name, value)
        self.allowed_size = None

    def _cmp_key(self):
        """
        Lowkey a mess of a method honestly, just ignore it
        """
        colours = []
        for square in self.get_squares():
            c = square.get_colour()
            if c is None:
                return None
            colours.append(c)

        red_count = colours.count("red")
        blue_count = colours.count("blue")

        if self.allowed_size is not None and red_count == self.allowed_size:
            return tuple(i for i, c in enumerate(colours) if c == "red")

        if self.allowed_size is not None and blue_count == self.allowed_size:
            return tuple(i for i, c in enumerate(colours) if c == "blue")

        return tuple(colours)

    def __eq__(self, other):
        """Also doesnt really work but we shall ignore it because it isnt used for generation currently LOL"""
        if not isinstance(other, RowColumnParent):
            return NotImplemented
        cmp_key = self._cmp_key()
        other_cmp_key = other._cmp_key()
        if cmp_key is None or other_cmp_key is None:
            return False
        return cmp_key == other_cmp_key


    def set_allowed_size(self):
        # sets the maximum of a colour in the row
        self.allowed_size = math.ceil(len(self.get_squares()) / 2)

    def check_row_critera(self):
        """makes sure there are maximum of allowed_size colours in a row"""
        red, blue, uncoloured = self.count_colours()
        if blue > self.allowed_size:
            return False
        elif red > self.allowed_size:
            return False
        return True

    def get_squares(self):
        """gets all squares in the row/column"""
        if hasattr(self, "row"):
            return self.row
        elif hasattr(self, "column"):
            return self.column
        else:
            raise AttributeError("Object has neither row nor column")

    def count_colours(self):
        """Gets the colour count of the row, kinda depricated because you can use get_colour_counts(row.row) or get_colour_counts(column.column)"""
        red = 0
        blue = 0
        uncoloured = 0
        # iterate the actual square objects
        for square in self.get_squares():
            if square.get_colour() == "blue":
                blue += 1
            elif square.get_colour() == "red":
                red += 1
            else:
                uncoloured += 1
        return red, blue, uncoloured


class UrjoRow(RowColumnParent):
    """row object inheriting directly from the rowcolumn parent"""
    attribute_name = "row"

class UrjoColumn(RowColumnParent):
    """column object inheriting directly from the rowcolumn parent"""
    attribute_name = "column"

def lines_different(line_1, line_2):
    """returns False if two lines are the same, to be honest dont trust this due to eq and cmp_key not really working"""
    for i, sq in enumerate(line_1):
        if sq.get_colour() != line_2[i].get_colour():
            return True
    return False


def not_identical(lst, index):
    """checks if the lines around it are identical"""
    if index > 0:
        if lst[index-1] == lst[index]:
            return False
    if index < (len(lst)-1):
        if lst[index + 1] == lst[index]:
            return False
    return True

def get_colour_counts(slots):
    """counts each colour in the provided slots"""
    red = 0
    blue = 0
    uncoloured = 0
    for slot in slots:
        if slot is not None:
            if slot.get_colour() == "red":
                red +=1
            if slot.get_colour() == "blue":
                blue +=1
            if slot.get_colour() == None:
                uncoloured +=1
    return red, blue, uncoloured

def not_colour(colour):
    """if blue returns red if red returns blue otherwise fails"""
    if colour == "blue":
        return "red"
    if colour == "red":
        return "blue"
    print("you tried to invert ", colour)
    raise Exception("that is not a valid colour")

def check_row_and_column(square):
    """checks the row and column for a slot"""
    if square.row.check_row_critera() and square.column.check_row_critera():
        return True
    return False

def fill_single_number(number):
    """
    fills the number cell and/or its surrounding slots and returns whether it has changed anything and
     what it has changed if it has
    """

    if number is None:
        return False, []

    target = number.get_number()
    if target is None:
        return False, []

    board = number.board
    surrounding_all = board.get_surrounding_slots(number)
    surrounding = [s for s in surrounding_all if s is not None]
    total = len(surrounding)

    # Should use get_colour_counts instead
    red = blue = uncol = 0
    for slt in surrounding:
        colour = slt.get_colour()
        if colour == "red":
            red += 1
        elif colour == "blue":
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

    # possibly determine the number cell's colour
    def feasible_if_colour(colour):
        if colour == "red":
            same_count, opp_count = red, blue
        else:
            same_count, opp_count = blue, red
        if same_count > required_same or same_count + uncol < required_same:
            return False
        if opp_count > required_opp or opp_count + uncol < required_opp:
            return False
        return True

    num_colour = number.get_colour()
    if num_colour is None:
        can_red = feasible_if_colour("red")
        can_blue = feasible_if_colour("blue")
        if can_red != can_blue:
            number.colour = "red" if can_red else "blue"
            number.hidden_bool = False
            changed = True
            filled_slots.append(number)
            num_colour = number.colour
        elif not (can_red or can_blue):
            return False, []

    if num_colour is None:
        return changed, filled_slots

    # forced fills among surrounding slots due to number

    if num_colour == "red":
        same, opp = red, blue
        same_col, opp_col = "red", "blue"
    else:
        same, opp = blue, red
        same_col, opp_col = "blue", "red"

    # same meets target (unassigned must be opposite)
    if same == required_same and uncol > 0:
        for s in surrounding:
            if s.get_colour() is None:
                s.colour = opp_col
                s.hidden_bool = False
                changed = True
                filled_slots.append(s)
        return changed, filled_slots

    # opposite meets target (unassigned must be same)
    if opp == required_opp and uncol > 0:
        for s in surrounding:
            if s.get_colour() is None:
                s.colour = same_col
                s.hidden_bool = False
                changed = True
                filled_slots.append(s)
        return changed, filled_slots

    # same + uncol == required_same (all unassigned required to be the same)
    if same + uncol == required_same and uncol > 0:
        for s in surrounding:
            if s.get_colour() is None:
                s.colour = same_col
                s.hidden_bool = False
                changed = True
                filled_slots.append(s)
        return changed, filled_slots

    # opposite + uncol == required_opp (all unassigned opposite colour)
    if opp + uncol == required_opp and uncol > 0:
        for s in surrounding:
            if s.get_colour() is None:
                s.colour = opp_col
                changed = True
                filled_slots.append(s)
        return changed, filled_slots

    # Can't fill any slots
    return changed, filled_slots






class UrjoBoard():
    """The Urjo puzzle, made up of rows and columns"""
    def __init__(self, rows=[], columns=[]):
        self.rows = rows
        self.columns = columns
        self.numbered_slots = []
        self.all_numbers = []
        self.all_squares = [] # Technically you could just use all_numbers and not double store this but it makes it easier to read and comprehend imo
        self.contradiction_count = 0
        self.removed_by_identical = 0

    def __str__(self):
        """how a puzzle prints out, for testing purposes"""
        lines = []
        for row in self.rows:
            line = []
            for square in row.row:
                if square.colour == "blue":
                    line.append("b")
                elif square.colour == "red":
                    line.append("r")
                elif square.get_colour() is None:
                    line.append(".")
                else:
                    line.append("?")
            lines.append(" ".join(line))
        return "\n".join(lines)

    @classmethod
    def from_url(cls, url_str, dim1, dim2):
        """converts a url into a urjo puzzle"""
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if len(url_str) != dim1 * dim2:
            raise ValueError("URL length does not match provided dimensions")

        board = cls()
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
            colour_bit = (value >> 1) & 1
            num_val = value >> 2

            sq = board.all_squares[idx]

            sq.colour = "blue" if colour_bit == 0 else "red"

            sq.hidden_bool = (visible_bit == 0)

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

        board.all_numbers = [sq for sq in board.all_squares if sq.number is not None]

        return board

    def snapshot_state(self):
        """stores the current board to revert too later"""
        snap = []
        for row in self.rows:
            for sq in row.get_squares():
                snap.append((sq, sq.colour, sq.hidden_bool))
        return snap

    def restore_state(self, snapshot):
        """reverts to the saved board"""
        for sq, col, hidden in snapshot:
            sq.colour = col
            sq.hidden_bool = hidden

    def hide_numbers(self, remaining_numbers):
        """hides all but remaining_numbers numbers"""
        random.shuffle(self.all_numbers)
        for i,number in enumerate(self.all_numbers):
             if i < remaining_numbers:
                 pass
             else:
                number.number_hidden = True

    def get_surrounding_slots(self, square):
        """returns the surrounding slots around a square"""
        r = square.row_index
        c = square.column_index
        rows = len(self.rows)
        cols = len(self.columns)

        def at(rr, cc):
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

    def get_number(self, slot):
        """gets the number for a slot, doesnt work if not all slots are coloured"""
        surrounding_slots = self.get_surrounding_slots(slot)
        colour = slot.colour
        total = 0
        for square in surrounding_slots:
            if square is not None:
                if square.colour == colour:
                    total +=1
        slot.number = total

    def fill_numbers(self):
        """puts all numbers on the full board"""
        for row in self.rows:
            for square in row.row:
                self.get_number(square)

    def number_check(self, number):
        """checks if the number rule is violated"""
        integer = number.get_number()
        if integer is None:
            return True

        red, blue, uncoloured = get_colour_counts(self.get_surrounding_slots(number))
        surrounding = red + blue + uncoloured

        # impossible number
        if integer < 0 or integer > surrounding:
            return False

        def feasible(required_same, same_count, opp_count, uncol):
            """
            checks the feasibility for a single colour
            """
            # current cannot exceed target
            if same_count > required_same:
                return False
            # even if all uncoloured become same, cannot reach target
            if same_count + uncol < required_same:
                return False

            required_opp = surrounding - required_same
            if opp_count > required_opp:
                return False
            if opp_count + uncol < required_opp:
                return False

            return True

        colour = number.get_colour()

        if colour is not None:
            if colour == "blue":
                return feasible(integer, blue, red, uncoloured)
            elif colour == "red":
                return feasible(integer, red, blue, uncoloured)
            else:
                return False
        else:
            ok_blue = feasible(integer, blue, red, uncoloured)
            ok_red = feasible(integer, red, blue, uncoloured)
            return ok_blue or ok_red

    def to_url_format(self):
        """sends the current puzzle into a url format"""
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        chars = []

        for row in self.rows:
            for sq in row.get_squares():
                if sq.number is not None and not sq.number_hidden:
                    num_val = sq.number + 1
                else:
                    num_val = 0

                if num_val > 15:
                    raise ValueError("Number too large to encode (max 15)") # Never encountered in real world scenarios

                colour_bit = 0 if sq.colour == "blue" else 1

                visible_bit = 0 if sq.hidden_bool else 1

                value = (num_val << 2) | (colour_bit << 1) | visible_bit

                chars.append(alphabet[value])

        return "".join(chars)

    def fill_board_backtracking(self, randomize_colours=True):
        """colour the whole board using backtracking so no row or column violates allowed_size, fill rules, or,
         creates identical adjacent rows/columns. this doesnt take numbers into account at all, only filling a possible
         colour arangement
        """
        squares = [sq for row in self.rows for sq in row.get_squares()]

        def backtrack(index=0):
            if index >= len(squares):
                return True

            square = squares[index]
            if square.colour is not None:
                return backtrack(index + 1)

            colours = ["red", "blue"]
            if randomize_colours:
                random.shuffle(colours)

            row_sqs = square.row.get_squares()
            col_sqs = square.column.get_squares()

            for colour in colours:
                row_snapshot = [sq.colour for sq in row_sqs]
                col_snapshot = [sq.colour for sq in col_sqs]

                square.colour = colour

                # capture both the boolean and the list of squares that were auto-filled
                row_filled, row_changed = self.fill_row(square.row)
                col_filled, col_changed = self.fill_column(square.column)

                # run all checks
                checks_ok = True
                if not square.row.check_row_critera():
                    checks_ok = False
                if not square.column.check_row_critera():
                    checks_ok = False

                # check adjacent rows/columns for identity regardless of fill
                if square.row_index > 0:
                    if self.rows[square.row_index - 1] == square.row:
                        checks_ok = False
                if square.row_index < len(self.rows) - 1:
                    if self.rows[square.row_index + 1] == square.row:
                        checks_ok = False
                if square.column_index > 0:
                    if self.columns[square.column_index - 1] == square.column:
                        checks_ok = False
                if square.column_index < len(self.columns) - 1:
                    if self.columns[square.column_index + 1] == square.column:
                        checks_ok = False

                if row_filled and not not_identical(self.rows, square.row_index):
                    checks_ok = False
                if col_filled and not not_identical(self.columns, square.column_index):
                    checks_ok = False


                for changed in row_changed:
                    if not changed.column.check_row_critera():
                        checks_ok = False
                        break
                    if not self.check_identical(changed):
                        checks_ok = False
                        break

                if checks_ok:
                    for changed in col_changed:
                        if not changed.row.check_row_critera():
                            checks_ok = False
                            break
                        if not self.check_identical(changed):
                            checks_ok = False
                            break


                if checks_ok:
                    if backtrack(index + 1):
                        return True  # success

                # restore snapshots
                for sq, old in zip(row_sqs, row_snapshot):
                    sq.colour = old
                for sq, old in zip(col_sqs, col_snapshot):
                    sq.colour = old
                square.colour = None

            return False  # no colour worked so backtrack

        return backtrack(0)


    def fill_row(self, row):
        """fills a row if it can be filled with a colour"""
        return self.__fill__(row, math.ceil(len(row.row)/2))

    def fill_column(self, column):
        """fills a column if it can be filled with a colour"""
        return self.__fill__(column, math.ceil(len(column.column)/2))

    def __fill__(self, obj, max):
        """fills an object will required remaining colours if possible else does nothing"""
        red, blue, uncoloured = obj.count_colours()
        squares = []
        if red == max:
            for square in obj.get_squares():
                if square.get_colour() is None:  # uses get_colour(), so only visiable colours are counted, be careful
                    square.colour = "blue"
                    square.hidden_bool = False
                    squares.append(square)

            return True, squares

        if blue == max:
            for square in obj.get_squares():
                if square.get_colour() is None:  # uses get_colour(), so only visiable colours are counted, be careful
                    square.colour = "red"
                    square.hidden_bool = False
                    squares.append(square)

            return True, squares

        return False, []

    def create_full_board(self, dim1, dim2):
        """Creates a full board of colours and numbers"""
        self.rows = [UrjoRow([]) for _ in range(dim2)]
        self.columns = [UrjoColumn([]) for _ in range(dim1)]
        self.all_squares = []
        self.all_numbers = []

        for y in range(dim2):
            for x in range(dim1):
                new_square = UrjoSquare(self, None, y, x)
                new_square.row = self.rows[y]
                new_square.column = self.columns[x]
                self.rows[y].row.append(new_square)
                self.columns[x].column.append(new_square)
                self.all_squares.append(new_square)
                self.all_numbers.append(new_square)

        for row in self.rows:
            row.set_allowed_size()
        for column in self.columns:
            column.set_allowed_size()

        if not self.fill_board_backtracking():
            raise ValueError("Unable to colour board with current constraints") # mostly only happens if the board is weirdly shaped in a way that makes the rules not possible

    def uncolour_square(self, square, number_checks=True,row_checks=True, identical_checks=True, contradiction_count=1, max_steps_without_info=4):
        """sees if a square can be uncoloured and the information recovered due to the other colour being impossible to be there"""
        if self.can_be_colour(square, not_colour(square.colour), number_checks,row_checks, identical_checks, contradiction_count, original_contradiction=contradiction_count, max_steps_without_info=max_steps_without_info):
            return False
        square.hidden_bool = True
        return True

    def check_identical(self, slot):
        """checks for identicality"""
        # row checks (compare current row to row above and below if they exist)
        r_idx = slot.row_index
        if r_idx > 0:
            if self.rows[r_idx - 1] == slot.row:
                return False
        if r_idx < len(self.rows) - 1:
            if self.rows[r_idx + 1] == slot.row:
                return False

        # column checks (compare current column to column left and right if they exist)
        c_idx = slot.column_index
        if c_idx > 0:
            if self.columns[c_idx - 1] == slot.column:
                return False
        if c_idx < len(self.columns) - 1:
            if self.columns[c_idx + 1] == slot.column:
                return False

        return True

    def can_be_colour(self, slot, colour,
                      number_checks=True, row_checks=True, identical_checks=True,
                      contradiction_count=1, original_contradiction=1, max_steps_without_info=4):
        # memoization: currently removed due to it causing impossible puzzles
        memo = {}


        # snapshot full board state as random colours are being changed
        state = self.snapshot_state()

        original = slot.colour
        original_hidden = slot.hidden_bool

        # seeing what happens if it was the other colour
        slot.colour = colour
        slot.hidden_bool = False

        # filling in all rows and columns that you can with the new information
        queue = deque([slot])
        queued_ids = {id(slot)}
        processed_ids = set()
        processed_numbers = set()

        while queue:
            cur = queue.popleft()
            cid = id(cur)
            queued_ids.discard(cid)
            processed_ids.add(cid)
            if row_checks:
                row_changed = self.fill_row(cur.row)[1]
                col_changed = self.fill_column(cur.column)[1]

                for ch in row_changed:
                    fid = id(ch)
                    if fid not in processed_ids and fid not in queued_ids:
                        queue.append(ch)
                        queued_ids.add(fid)
                for ch in col_changed:
                    fid = id(ch)
                    if fid not in processed_ids and fid not in queued_ids:
                        queue.append(ch)
                        queued_ids.add(fid)

            if number_checks:
                surrounding = self.get_surrounding_slots(cur)
                for slt in surrounding:
                    if slt is None:
                        continue
                    if slt.get_number() is None:
                        continue
                    sid = id(slt)
                    if sid in processed_numbers:
                        continue
                    processed_numbers.add(sid)

                    changed, filled = fill_single_number(slt)
                    if changed:
                        for f in filled:
                            fid = id(f)
                            if fid not in processed_ids and fid not in queued_ids:
                                queue.append(f)
                                queued_ids.add(fid)

        # did we anything get added? used for higher level puzzles to ignore recusion steps where nothing significant happened at a specific recursion step
        did_expansion = len(processed_ids) > 1

        # run the checks to see if we can quickly conclude anything from the slot
        checks = []
        if number_checks:
            checks.append(self.check_surrounding_numbers(slot))
        if row_checks:
            checks.append(check_row_and_column(slot))
        if identical_checks:
            checks.append(self.check_identical(slot))
            if contradiction_count == original_contradiction and not checks[-1]:
                if all(checks[:-1]):
                    self.removed_by_identical += 1

        if not all(checks):
            # restore and return false a check fails
            self.restore_state(state)
            return False

        # only continue deeper if something else got filled in if you are passed some step count in
        should_continue = did_expansion or (contradiction_count + max_steps_without_info > original_contradiction)

        # contradiction recursion step
        if contradiction_count > 0 and should_continue:
            change_available = [square for square in self.all_squares if square.get_colour() is None]
            k = min(10000, len(change_available))
            samples = random.sample(change_available, k) if k > 0 else []
            for sample in samples:
                ok_blue = self.can_be_colour(sample, "blue",
                                             number_checks, row_checks, identical_checks,
                                             contradiction_count - 1, original_contradiction)
                ok_red = self.can_be_colour(sample, "red",
                                            number_checks, row_checks, identical_checks,
                                            contradiction_count - 1, original_contradiction)
                if not ok_blue and not ok_red:
                    if contradiction_count == original_contradiction:
                        self.contradiction_count += 1
                    self.restore_state(state)

                    return False

        # restore and return True
        self.restore_state(state)

        return True

    def check_surrounding_numbers(self, slot):
        """
        return False if any surrounding numbered cell's checks doesnt work
        """
        for number in self.get_surrounding_slots(slot):
            if number is not None:
                if not self.number_check(number):
                    return False
        return True

    def unfill(self, integer):
        """duplicate function for unfilling numbers, dont know why I made two, this code has gotten so long im not noticing a lot"""
        random.shuffle(self.all_numbers)

        for i, sq in enumerate(self.all_numbers):
            if i < integer:
                sq.number_hidden = False
            else:
                sq.number_hidden = True

    def create_puzzle(self, dim1, dim2, number_checks=True, row_checks=True, identical_checks=False, contradiction_count=1, number_of_numbers=0, max_steps_without_info=4): # IDENTICAL CHECKS DONT WORK DONT TURN ON
        """Creates a full puzzle from the inputs"""

        self.create_full_board(dim1, dim2)

        for row in self.rows:
            row.set_allowed_size()

        for column in self.columns:
            column.set_allowed_size()

        self.fill_numbers()

        self.unfill(number_of_numbers)

        random.shuffle(self.all_squares)
        for slot in self.all_squares:
            self.uncolour_square(slot, number_checks, row_checks, identical_checks, contradiction_count, max_steps_without_info=max_steps_without_info)

    def true_check(self):
        """only for testing purposes to make sure the row/column counts didnt mess up which it was earlier"""
        puzzle = self.to_url_format()
        checks = []

        for row in self.rows:
            for square in row.row:
                square.hidden_bool = False
            checks.append(row.check_row_critera())


        for column in self.columns:
            for square in column.column:
                square.hidden_bool = False
            checks.append(column.check_row_critera())
        if not all(checks):
            print("CHECK FAILED:", puzzle)


while True:
    urjo = UrjoBoard()
    urjo.create_puzzle(8,8, number_of_numbers=5, contradiction_count=2)
    print(urjo.to_url_format(), urjo.contradiction_count)

    #if urjo.contradiction_count > 5 :
    #    print(urjo.to_url_format(), urjo.contradiction_count)
    #if urjo.removed_by_identical > 0:
    #    print(urjo.to_url_format(), urjo.removed_by_identical)
    urjo.true_check()

