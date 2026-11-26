from disc_color import DiscColor


class Board:
    def __init__(self, rows: int = 6, cols: int = 7):
        if rows < 4 or cols < 4:
            raise ValueError("Board must be at least 4x4")
        self.rows = rows
        self.cols = cols
        self.grid = [[DiscColor.EMPTY for _ in range(cols)] for _ in range(rows)]

    def can_place(self, column: int) -> bool:
        return 0 <= column < self.cols and self.grid[0][column] == DiscColor.EMPTY

    def place_disc(self, column: int, color: DiscColor) -> int:
        if not self.can_place(column):
            return -1
        for row in range(self.rows - 1, -1, -1):
            if self.grid[row][column] == DiscColor.EMPTY:
                self.grid[row][column] = color
                return row
        return -1

    def clear_cell(self, row: int, col: int) -> None:
        self.grid[row][col] = DiscColor.EMPTY

    def is_full(self) -> bool:
        return all(not self.can_place(col) for col in range(self.cols))

    def check_win(self, row: int, col: int, color: DiscColor) -> bool:
        return (
            self._count_connected(row, col, 0, 1, color) >= 4
            or self._count_connected(row, col, 1, 0, color) >= 4
            or self._count_connected(row, col, 1, 1, color) >= 4
            or self._count_connected(row, col, 1, -1, color) >= 4
        )

    def _count_connected(self, row: int, col: int, dr: int, dc: int, color: DiscColor) -> int:
        return 1 + self._count_dir(row, col, dr, dc, color) + self._count_dir(row, col, -dr, -dc, color)

    def _count_dir(self, row: int, col: int, dr: int, dc: int, color: DiscColor) -> int:
        count = 0
        r, c = row + dr, col + dc
        while 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == color:
            count += 1
            r += dr
            c += dc
        return count
