from board import *
from typing import List
from collections import deque

class UrjoGenerator():
    board: Board

    def __init__(self):
        self.board = Board()
        self.removed_by_identical: int = 0

    def number_check(self, slot: Cell):
        """Checks if the number rule is violated"""
        number = slot.get_number()
        if number is None:
            return True

        if slot is None:
            raise Exception("slot cannot be None!")

        if slot.row is None:
            raise Exception("Cannot use outside of a row")

        red, blue, uncolored = get_color_counts(
            list(self.board.get_surrounding_slots(slot)))
        surroundingCellCount = red + blue + uncolored

        # impossible number
        if number < 0 or number > surroundingCellCount:
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

            required_opp = surroundingCellCount - required_same
            if opp_count > required_opp:
                return False
            if opp_count + uncol < required_opp:
                return False

            return True

        color = slot.get_color()

        if color is not None:
            if color == "blue":
                return feasible(number, blue, red, uncolored)
            elif color == "red":
                return feasible(number, red, blue, uncolored)
            else:
                return False
        else:
            ok_blue = feasible(number, blue, red, uncolored)
            ok_red = feasible(number, red, blue, uncolored)
            return ok_blue or ok_red

    def fill_board_backtracking(self, randomize_colors=True):
        """
        Color the whole board using backtracking so no row or column violates allowed_size, fill rules, or,
        creates identical adjacent rows/columns. this doesnt take numbers into account at all, only filling a possible
        color arangement
        """
        cells: List[Cell] = [
            sq for row in self.board.rows for sq in row.get_cells()]

        def backtrack(index=0):
            if index >= len(cells):
                return True

            currentCell: Cell | None = cells[index]
            if currentCell.color is not None:
                return backtrack(index + 1)

            colors: List[Color] = ["red", "blue"]
            if randomize_colors:
                random.shuffle(colors)

            if currentCell.row is None or currentCell.column is None:
                raise Exception("Cannot use on a sole cell!")

            currentRow: List[Cell] = currentCell.row.get_cells()
            currentCol: List[Cell] = currentCell.column.get_cells()

            for color in colors:
                row_snapshot: List[Color | None] = [
                    sq.color for sq in currentRow]
                col_snapshot: List[Color | None] = [
                    sq.color for sq in currentCol]

                currentCell.color = color

                # capture both the boolean and the list of squares that were auto-filled
                row_filled, row_changed = self.board.fill_half_full_row(
                    currentCell.row)
                col_filled, col_changed = self.board.fill_half_full_column(
                    currentCell.column)

                # run all checks
                checks_ok = True
                if not currentCell.row.check_color_count():
                    checks_ok = False
                if not currentCell.column.check_color_count():
                    checks_ok = False

                # # check adjacent rows/columns for identity regardless of fill
                # if currentCell.posX > 0:
                #     if self.board.rows[currentCell.posX - 1] == currentCell.row:
                #         checks_ok = False
                # if currentCell.posX < len(self.board.rows) - 1:
                #     if self.board.rows[currentCell.posX + 1] == currentCell.row:
                #         checks_ok = False
                # if currentCell.posY > 0:
                #     if self.board.columns[currentCell.posY - 1] == currentCell.column:
                #         checks_ok = False
                # if currentCell.posY < len(self.board.columns) - 1:
                #     if self.board.columns[currentCell.posY + 1] == currentCell.column:
                #         checks_ok = False

                # if row_filled and not nonIdentical(self.board.rows, currentCell.posX):
                #     checks_ok = False
                # if col_filled and not nonIdentical(self.board.columns, currentCell.posY):
                #     checks_ok = False

                for change in row_changed:
                    # Commented out because i don't know where this function went
                    col: UrjoColumn = change.column
                    if not col.check_color_count():
                        checks_ok = False
                        break
                    # if not self.board.check_identical(change):
                    #     checks_ok = False
                    #     break

                if checks_ok:
                    for change in col_changed:
                        row: UrjoRow = change.row
                        if not row.check_color_count():
                            checks_ok = False
                            break
                        # if not self.board.check_identical(change):
                        #     checks_ok = False
                        #     break

                if checks_ok:
                    if backtrack(index + 1):
                        return True  # success

                # restore snapshots
                for sq, old in zip(currentRow, row_snapshot):
                    sq.color = old
                for sq, old in zip(currentCol, col_snapshot):
                    sq.color = old
                currentCell.color = None

            return False  # no color worked so backtrack

        return backtrack(0)

    def fill_row(self, row: UrjoRow):
        """Fills a row if it can be filled with a color"""
        return self.__fill__(row, math.ceil(len(row.cells)/2))

    def fill_column(self, column: UrjoColumn):
        """Fills a column if it can be filled with a color"""
        return self.__fill__(column, math.ceil(len(column.cells)/2))

    def __fill__(self, obj: UrjoRow | UrjoColumn, max):
        """Fills an object will required remaining colors if possible, else does nothing"""
        red, blue, uncolored = obj.count_colors()
        squares = []
        if red == max:
            for square in obj.get_cells():
                if square.get_color() is None:  # uses get_color(), so only visiable colors are counted, be careful
                    square.color = "blue"
                    square.hidden = False
                    squares.append(square)

            return True, squares

        if blue == max:
            for square in obj.get_cells():
                if square.get_color() is None:  # uses get_color(), so only visiable colors are counted, be careful
                    square.color = "red"
                    square.hidden = False
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
            for square in row.cells:
                square.hidden = False
            checks.append(row.check_color_count())

        for column in self.board.columns:
            for square in column.cells:
                square.hidden = False
            checks.append(column.check_color_count())
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
        self.all_squares: List[Cell] = []
        self.all_numbers: List[Cell] = []

        for y in range(dim2):
            for x in range(dim1):
                new_square = Cell(self.board, None, y, x)
                new_square.row = self.board.rows[y]
                new_square.column = self.board.columns[x]
                self.board.rows[y].cells.append(new_square)
                self.board.columns[x].cells.append(new_square)
                self.board.all_squares.append(new_square)
                self.board.all_numbers.append(new_square)

        for row in self.board.rows:
            row.set_allowed_size()
        for column in self.board.columns:
            column.set_allowed_size()

        if not self.fill_board_backtracking():
            # mostly only happens if the board is weirdly shaped in a way that makes the rules not possible
            raise ValueError("Unable to color board with current constraints")

    def uncolor_square(self, square: Cell, number_checks=True, row_checks=True, identical_checks=True, contradiction_count=1, max_steps_without_info=4):
        """Sees if a square can be uncolored and the information recovered due to the other color being impossible to be there"""
        if self.can_be_color(square, invert_color(square.color), number_checks, row_checks, identical_checks, contradiction_count, original_contradiction=contradiction_count, max_steps_without_info=max_steps_without_info):
            return False
        square.hidden = True
        return True

    def check_identical(self, slot: Cell):
        """Checks wether neighboring lines are the same"""
        # row checks (compare current row to row above and below if they exist)
        r_idx = slot.posX
        if r_idx > 0:
            if self.board.rows[r_idx - 1] == slot.row:
                return False
        if r_idx < len(self.board.rows) - 1:
            if self.board.rows[r_idx + 1] == slot.row:
                return False

        # column checks (compare current column to column left and right if they exist)
        c_idx = slot.posY
        if c_idx > 0:
            if self.board.columns[c_idx - 1] == slot.column:
                return False
        if c_idx < len(self.board.columns) - 1:
            if self.board.columns[c_idx + 1] == slot.column:
                return False

        return True

    def can_be_color(self, cell: Cell, color: Literal["red", "blue"] | None,
                     number_checks=True, row_checks=True, identical_checks=True,
                     contradiction_count=1, original_contradiction=1, max_steps_without_info=4):
        # memoization: currently removed due to it causing impossible puzzles
        memo = {}

        # snapshot full board state as random colors are being changed
        state = self.board.snapshot_state()

        originalColor = cell.color
        originalHidden = cell.hidden

        # seeing what happens if it was the other color
        cell.color = color
        cell.hidden = False

        # filling in all rows and columns that you can with the new information
        queue = deque([cell])
        queued_ids = {id(cell)}
        processed_ids = set()
        processed_numbers = set()

        while queue:
            currentCell = queue.popleft()
            currentID = id(currentCell)
            queued_ids.discard(currentID)
            processed_ids.add(currentID)
            if row_checks:
                row_changed = self.board.fill_half_full_row(currentCell.row)[1]
                col_changed = self.board.fill_half_full_column(currentCell.column)[1]

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
                surrounding = self.board.get_surrounding_slots(currentCell)
                for slt in surrounding:
                    if slt is None:
                        continue
                    if slt.get_number() is None:
                        continue
                    sid = id(slt)
                    if sid in processed_numbers:
                        continue
                    processed_numbers.add(sid)

                    changed, filled = self.board.tryToFill(slt)
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
            checks.append(self.check_surrounding_numbers(cell))
        if row_checks:
            checks.append(check_row_and_column(cell))
        if identical_checks:
            checks.append(self.board.check_identical(cell))
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
                        self.board.contradiction_count += 1
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
