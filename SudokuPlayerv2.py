import sys, pygame as pg
import numpy as np
import time
pg.init()


class Grid:
    number_grid = np.array([
        [7, 0, 1, 3, 0, 9, 0, 0, 5],
        [0, 0, 0, 0, 0, 1, 6, 0, 4],
        [5, 0, 4, 0, 0, 0, 7, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0],
        [8, 0, 7, 6, 0, 4, 9, 0, 0],
        [0, 1, 0, 5, 0, 0, 3, 0, 6],
        [9, 0, 3, 0, 6, 5, 0, 8, 7],
        [0, 5, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 8, 3, 0, 0, 0, 9]
    ])
    # number_grid = np.zeros((9, 9), dtype=int)

    def __init__(self, width, height):
        self.rows = 9
        self.cols = 9
        self.width = width
        self.height = height
        self.buffer = 15
        self.gap = (self.width - 2 * self.buffer) // self.cols
        self.squares = [
            [Square(self.number_grid[i][j], i, j, self.gap, self.buffer) for j in range(len(self.number_grid[i]))]
            for i in range(len(self.number_grid))]
        self.selected = [0, 0]
        self.selection_update()
        for squares in self.squares:
            for square in squares:
                self.not_possibles(square)
        
    def selection_update(self, direction=None, selected=(0, 0)):
        if not direction:
            self.squares[self.selected[1]][self.selected[0]].selected = False
            self.selected[1], self.selected[0] = selected[0], selected[1]

        self.squares[self.selected[1]][self.selected[0]].selected = False
        if direction == 'left' and self.selected[0] > 0:
            self.selected[0] -= 1
        elif direction == 'right' and self.selected[0] < self.cols - 1:
            self.selected[0] += 1
        elif direction == 'up' and self.selected[1] > 0:
            self.selected[1] -= 1
        elif direction == 'down' and self.selected[1] < self.rows - 1:
            self.selected[1] += 1

        self.squares[self.selected[1]][self.selected[0]].selected = True
            
    def draw(self, win):
        for i in range(10):
            weight = 5 if i % 3 == 0 else 3

            pg.draw.line(
                win,
                pg.Color('black'),
                (self.buffer + i * self.gap, self.buffer),
                (self.buffer + i * self.gap, self.width - self.buffer),
                weight
            )
            pg.draw.line(
                win,
                pg.Color('black'),
                (self.buffer, self.buffer + i * self.gap),
                (self.width - self.buffer, self.buffer + i * self.gap),
                weight
            )

    def value_update(self, val):
        self.squares[self.selected[1]][self.selected[0]].change_val(val, self.number_grid)

    def not_possibles(self, current_square):
        for num in range(1, 10):
            if not self.is_possible_quick(current_square, num):
                current_square.not_possible.append(num)

    def is_possible(self, current_square, num, win):
        row, col = current_square.row, current_square.col
        current_square.temp = num
        # window_update(win, self)
        # pg.display.update()
        if num not in current_square.not_possible:
            for i, squares in enumerate(self.squares):
                if current_square.temp == squares[col].val and row != i:
                    squares[col].bad_square = True
                    current_square.bad_num = True
                    window_update(win, self)
                    pg.display.update()
                    squares[col].bad_square = False
                    current_square.bad_num = False
                    current_square.temp = 0
                    time.sleep(0.3)
                    return False
            for i, square in enumerate(self.squares[row]):
                if current_square.temp == square.val and col != i:
                    square.bad_square = True
                    current_square.bad_num = True
                    window_update(win, self)
                    pg.display.update()
                    square.bad_square = False
                    current_square.bad_num = False
                    current_square.temp = 0
                    time.sleep(0.3)
                    return False

            square_left = (col // 3) * 3
            square_top = (row // 3) * 3
            for i in range(square_top, square_top + 3):
                for j in range(square_left, square_left + 3):
                    if self.squares[i][j].val == current_square.temp:
                        self.squares[i][j].bad_square = True
                        current_square.bad_num = True
                        window_update(win, self)
                        pg.display.update()
                        self.squares[i][j].bad_square = False
                        current_square.bad_num = False
                        current_square.temp = 0
                        time.sleep(0.3)
                        return False
        else:
            current_square.temp = 0
            return False
        current_square.temp = 0
        return True

    def is_possible_quick(self, current_square, num):
        row, col = current_square.row, current_square.col
        for i, squares in enumerate(self.squares):
            if num == squares[col].val and row != i:
                return False
        for i, square in enumerate(self.squares[row]):
            if num == square.val and col != i:
                return False

        square_left = (col // 3) * 3
        square_top = (row // 3) * 3
        for i in range(square_top, square_top + 3):
            for j in range(square_left, square_left + 3):
                if self.squares[i][j].val == num:
                    return False

        return True

    def is_solved(self):
        for row in self.number_grid:
            for i in row:
                if i == 0:
                    return False
        return True

    def solve(self, win):
        if self.is_solved():
            return True
        for i, rows in enumerate(self.squares):
            for j, square in enumerate(rows):
                if square.val == 0:
                    for num in range(1, 10):
                        self.selection_update(selected=(i, j))
                        if self.is_possible(square, num, win):
                            window_update(win, self)
                            pg.display.update()
                            square.change_val(num, self.number_grid)
                            if self.solve(win):
                                return True
                            square.change_val(0, self.number_grid)
                    return False


class Square:
    def __init__(self, val, row, col, width, buffer):
        self.val = val
        self.row = row
        self.col = col
        self.width = width
        self.buffer = buffer
        self.selected = False
        self.locked = True if val != 0 else False
        self.temp = 0
        self.bad_square = False
        self.bad_num = False
        self.done = False
        self.not_possible = []

    def draw(self, win):
        font = pg.font.SysFont(None, 80)
        x = self.col * self.width + self.buffer
        y = self.row * self.width + self.buffer
        color = (0, 0, 0) if self.locked else (100, 100, 120)
        if self.done and not self.locked:
            color = (0, 255, 0)

        if self.val != 0:
            n_text = font.render(str(self.val), True, color)
            win.blit(
                n_text,
                (x + (self.width // 2 - n_text.get_width() // 2), y + (self.width // 2 - n_text.get_height() // 2))
            )

        if self.temp != 0:
            if not self.bad_num:
                n_text = font.render(str(self.temp), True, (0, 255, 255))
            else:
                n_text = font.render(str(self.temp), True, (255, 0, 0))
            win.blit(
                n_text,
                (x + (self.width // 2 - n_text.get_width() // 2), y + (self.width // 2 - n_text.get_height() // 2))
            )

        if self.selected:
            pg.draw.rect(
                win,
                (0, 255, 255),
                pg.Rect(x, y, self.width, self.width),
                5,
                5
            )

        if self.bad_square:
            pg.draw.rect(
                win,
                (255, 0, 0),
                pg.Rect(x, y, self.width, self.width),
                5,
                5
            )

    def change_val(self, val, board):
        if not self.locked:
            self.val = val
            board[self.row][self.col] = val


def window_update(win, board):
    win.fill((255, 255, 255))
    board.draw(win)
    for row in board.squares:
        for square in row:
            square.draw(win)


def main():
    width = 750
    height = 750
    win = pg.display.set_mode((width, height))
    board = Grid(width, height)
    board.squares[0][0].selected = True

    while True:
        if board.is_solved():
            for squares in board.squares:
                for square in squares:
                    square.done = True
        for event in pg.event.get():
            if event.type == pg.QUIT:
                print(board.number_grid)
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    board.selection_update('left')
                elif event.key == pg.K_RIGHT:
                    board.selection_update('right')
                elif event.key == pg.K_UP:
                    board.selection_update('up')
                elif event.key == pg.K_DOWN:
                    board.selection_update('down')
                elif event.key == pg.K_BACKSPACE:
                    board.value_update(0)
                elif event.key == pg.K_1:
                    board.value_update(1)
                elif event.key == pg.K_2:
                    board.value_update(2)
                elif event.key == pg.K_3:
                    board.value_update(3)
                elif event.key == pg.K_4:
                    board.value_update(4)
                elif event.key == pg.K_5:
                    board.value_update(5)
                elif event.key == pg.K_6:
                    board.value_update(6)
                elif event.key == pg.K_7:
                    board.value_update(7)
                elif event.key == pg.K_8:
                    board.value_update(8)
                elif event.key == pg.K_9:
                    board.value_update(9)
                elif event.key == pg.K_SPACE:
                    board.solve(win)
            if pg.mouse.get_pressed()[0]:
                mouse = pg.mouse.get_pos()
                row = ((mouse[1] - board.buffer) // board.gap)
                col = ((mouse[0] - board.buffer) // board.gap)
                board.selection_update(selected=(row, col))

        window_update(win, board)
        pg.display.update()


main()
pg.quit()
#test