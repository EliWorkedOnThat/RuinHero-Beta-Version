#Imports
import tkinter as tk

#Calculate Tile Grid and Size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TILE_SIZE = 32

COLS = WINDOW_WIDTH // TILE_SIZE
ROWS = WINDOW_HEIGHT // TILE_SIZE

#Main Window
root = tk.Tk()
root.title("Ruine Hero")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)

#Canvas Setup
canvas = tk.Canvas(
    root,
    width = WINDOW_WIDTH,
    height = WINDOW_HEIGHT,
    bg = "black",
    highlightthickness=0
)
canvas.pack()

def draw_grid():
    for x in range(0, WINDOW_WIDTH, TILE_SIZE):
        canvas.create_line(x, 0, x, WINDOW_HEIGHT, fill="#333")
    for y in range(0, WINDOW_HEIGHT, TILE_SIZE):
        canvas.create_line(0, y, WINDOW_WIDTH, y, fill="#333")

draw_grid()

#Main Loop
root.mainloop()