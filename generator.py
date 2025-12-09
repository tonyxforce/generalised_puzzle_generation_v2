from board import *
from typing import List


class UrjoGenerator():
    """The Urjo puzzle, made up of rows and columns"""

    def __init__(self, rows: List[UrjoRow] = [], columns: List[UrjoColumn] = []):
        self.board = UrjoBoard()
        self.contradiction_count: int = 0
        self.removed_by_identical: int = 0

    def number_check(self, slot: UrjoSquare):
        """Checks if the number rule is violated"""
        integer = slot.get_number()
        if integer is None:
            return True

        red, blue, uncolored = get_color_counts(
            self.board.get_surrounding_slots(slot))
        surrounding = red + blue + uncolored

        # impossible number
        if integer < 0 or integer > surrounding:
            return False

        def feasible(required_same, same_count, opp_count, uncol):
            """
            Checks the feasibility for a single color
            """
            # current cannot exceed target
            if same_count > required_same:
                return False
            # even if all uncolored become same, cannot reach target
            if same_count + uncol < required_same:
                return False

            required_opp = surrounding - required_same
            if opp_count > required_opp:
                return False
            if opp_count + uncol < required_opp:
                return False

            return True

        color = slot.get_color()

        if color is not None:
            if color == "blue":
                return feasible(integer, blue, red, uncolored)
            elif color == "red":
                return feasible(integer, red, blue, uncolored)
            else:
                return False
        else:
            ok_blue = feasible(integer, blue, red, uncolored)
            ok_red = feasible(integer, red, blue, uncolored)
            return ok_blue or ok_red

    def fill_board_backtracking(self, randomize_colors=True):
        """
        Color the whole board using backtracking so no row or column violates allowed_size, fill rules, or,
        creates identical adjacent rows/columns. this doesnt take numbers into account at all, only filling a possible
        color arangement
        """
        squares = [sq for row in self.board.rows for sq in row.get_squares()]

        def backtrack(index=0):
            if index >= len(squares):
                return True

            square = squares[index]
            if square.color is not None:
                return backtrack(index + 1)

            colors = ["red", "blue"]
            if randomize_colors:
                random.shuffle(colors)

            row_sqs = square.row.get_squares()
            col_sqs = square.column.get_squares()

            for color in colors:
                row_snapshot = [sq.color for sq in row_sqs]
                col_snapshot = [sq.color for sq in col_sqs]

                square.color = color

                # capture both the boolean and the list of squares that were auto-filled
                row_filled, row_changed = self.board.fill_row(square.row)
                col_filled, col_changed = self.board.fill_column(square.column)

                # run all checks
                checks_ok = True
                if not square.row.check_row_critera():
                    checks_ok = False
                if not square.column.check_row_critera():
                    checks_ok = False

                # check adjacent rows/columns for identity regardless of fill
                if square.row_index > 0:
                    if self.board.rows[square.row_index - 1] == square.row:
                        checks_ok = False
                if square.row_index < len(self.board.rows) - 1:
                    if self.board.rows[square.row_index + 1] == square.row:
                        checks_ok = False
                if square.column_index > 0:
                    if self.board.columns[square.column_index - 1] == square.column:
                        checks_ok = False
                if square.column_index < len(self.board.columns) - 1:
                    if self.board.columns[square.column_index + 1] == square.column:
                        checks_ok = False

                if row_filled and not not_identical(self.board.rows, square.row_index):
                    checks_ok = False
                if col_filled and not not_identical(self.board.columns, square.column_index):
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
                    sq.color = old
                for sq, old in zip(col_sqs, col_snapshot):
                    sq.color = old
                square.color = None

            return False  # no color worked so backtrack

        return backtrack(0)

    def fill_row(self, row: UrjoRow):
        """Fills a row if it can be filled with a color"""
        return self.__fill__(row, math.ceil(len(row.row)/2))

    def fill_column(self, column: UrjoColumn):
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
                    square.hidden_bool = False
                    squares.append(square)

            return True, squares

        return False, []

    def unfill(self, integer: int):
        """Duplicate function for unfilling numbers, dont know why I made two, this code has gotten so long im not noticing a lot"""
        random.shuffle(self.all_numbers)

        for i, sq in enumerate(self.all_numbers):
            if i < integer:
                sq.number_hidden = False
            else:
                sq.number_hidden = True

    def true_check(self):
        """Only for testing purposes to make sure the row/column counts didn't mess up which it was earlier"""
        puzzle = self.board.to_url_format()
        checks = []

        for row in self.board.rows:
            for square in row.row:
                square.hidden = False
            checks.append(row.check_row_critera())

        for column in self.board.columns:
            for square in column.column:
                square.hidden = False
            checks.append(column.check_row_critera())
        if not all(checks):
            print("CHECK FAILED:", puzzle)

    # IDENTICAL CHECKS DONT WORK DONT TURN ON

    def create_puzzle(self, dim1: int, dim2: int, number_checks=True, row_checks=True, identical_checks=False, contradiction_count=1, number_of_numbers=0, max_steps_without_info=4):
        """Creates a full puzzle from the inputs"""

        self.create_full_board(dim1, dim2)

        for row in self.board.rows:
            row.set_allowed_size()

        for column in self.board.columns:
            column.set_allowed_size()

        self.board.fill_numbers()

        self.unfill(number_of_numbers)

        random.shuffle(self.board.all_squares)
        for slot in self.board.all_squares:
            self.uncolor_square(slot, number_checks, row_checks, identical_checks,
                                contradiction_count, max_steps_without_info=max_steps_without_info)
        return self.board

    def create_full_board(self, dim1: int, dim2: int):
        """Creates a full board of colors and numbers"""
        self.board.rows = [UrjoRow([]) for _ in range(dim2)]
        self.board.columns = [UrjoColumn([]) for _ in range(dim1)]
        self.all_squares: List[UrjoSquare] = []
        self.all_numbers: List[UrjoSquare] = []

        for y in range(dim2):
            for x in range(dim1):
                new_square = UrjoSquare(self.board, None, y, x)
                new_square.row = self.board.rows[y]
                new_square.column = self.board.columns[x]
                self.board.rows[y].row.append(new_square)
                self.board.columns[x].column.append(new_square)
                self.board.all_squares.append(new_square)
                self.board.all_numbers.append(new_square)

        for row in self.board.rows:
            row.set_allowed_size()
        for column in self.board.columns:
            column.set_allowed_size()

        if not self.fill_board_backtracking():
            # mostly only happens if the board is weirdly shaped in a way that makes the rules not possible
            raise ValueError("Unable to color board with current constraints")

    def uncolor_square(self, square: UrjoSquare, number_checks=True, row_checks=True, identical_checks=True, contradiction_count=1, max_steps_without_info=4):
        """Sees if a square can be uncolored and the information recovered due to the other color being impossible to be there"""
        if self.can_be_color(square, invert_color(square.color), number_checks, row_checks, identical_checks, contradiction_count, original_contradiction=contradiction_count, max_steps_without_info=max_steps_without_info):
            return False
        square.hidden = True
        return True

    def check_identical(self, slot: UrjoSquare):
        """Checks wether neighboring lines are the same"""
        # row checks (compare current row to row above and below if they exist)
        r_idx = slot.row_index
        if r_idx > 0:
            if self.board.rows[r_idx - 1] == slot.row:
                return False
        if r_idx < len(self.board.rows) - 1:
            if self.board.rows[r_idx + 1] == slot.row:
                return False

        # column checks (compare current column to column left and right if they exist)
        c_idx = slot.column_index
        if c_idx > 0:
            if self.board.columns[c_idx - 1] == slot.column:
                return False
        if c_idx < len(self.board.columns) - 1:
            if self.board.columns[c_idx + 1] == slot.column:
                return False

        return True

    def can_be_color(self, slot: UrjoSquare, color: Literal["red", "blue"],
                     number_checks=True, row_checks=True, identical_checks=True,
                     contradiction_count=1, original_contradiction=1, max_steps_without_info=4):
        # memoization: currently removed due to it causing impossible puzzles
        memo = {}

        # snapshot full board state as random colors are being changed
        state = self.board.snapshot_state()

        original = slot.color
        original_hidden = slot.hidden

        # seeing what happens if it was the other color
        slot.color = color
        slot.hidden = False

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
                row_changed = self.board.fill_row(cur.row)[1]
                col_changed = self.board.fill_column(cur.column)[1]

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
                surrounding = self.board.get_surrounding_slots(cur)
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

        # did anything get added? used for higher level puzzles to ignore recusion steps where nothing significant happened at a specific recursion step
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
            self.board.restore_state(state)
            return False

        # only continue deeper if something else got filled in if you are passed some step count in
        should_continue = did_expansion or (
            contradiction_count + max_steps_without_info > original_contradiction)

        # contradiction recursion step
        if contradiction_count > 0 and should_continue:
            change_available = [
                square for square in self.board.all_squares if square.get_color() is None]
            k = min(10000, len(change_available))
            samples = random.sample(change_available, k) if k > 0 else []
            for sample in samples:
                ok_blue = self.can_be_color(sample, "blue",
                                            number_checks, row_checks, identical_checks,
                                            contradiction_count - 1, original_contradiction)
                ok_red = self.can_be_color(sample, "red",
                                           number_checks, row_checks, identical_checks,
                                           contradiction_count - 1, original_contradiction)
                if not ok_blue and not ok_red:
                    if contradiction_count == original_contradiction:
                        self.contradiction_count += 1
                    self.board.restore_state(state)

                    return False

        # restore and return True
        self.board.restore_state(state)

        return True

    def check_surrounding_numbers(self, slot):
        """
        Check whether every surrounding numbered cell's checks pass
        """
        for slot in self.board.get_surrounding_slots(slot):
            if slot is not None:
                if not self.number_check(slot):
                    return False
        return True
