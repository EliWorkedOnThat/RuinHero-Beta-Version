#Imports
import tkinter as tk
from Maps import basic_map

#Calculate Tile Grid and Size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 672
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

#Mapping Tiles
map_data = basic_map

#Corresponding Tile to ID

tile_images = {
    0: tk.PhotoImage(file="TexturePack/Basic Tiles/Grass.png"),
    1: tk.PhotoImage(file="TexturePack/Basic Tiles/Water.png"),
    2: tk.PhotoImage(file="TexturePack/Basic Tiles/Stone.png"),
    3: tk.PhotoImage(file = "TexturePack/Ores/Diamond.png"),
    4: tk.PhotoImage(file = "TexturePack/Ores/Gold.png"),
    5: tk.PhotoImage(file = "TexturePack/Ores/Ruby.png"),
    6: tk.PhotoImage(file = "TexturePack/Basic Tiles/Sand.png")
}

#Draw Temporary Grid
def draw_grid():
    for x in range(0, WINDOW_WIDTH, TILE_SIZE):
        canvas.create_line(x, 0, x, WINDOW_HEIGHT, fill="#333")
    for y in range(0, WINDOW_HEIGHT, TILE_SIZE):
        canvas.create_line(0, y, WINDOW_WIDTH, y, fill="#333")

#Draw Map Function Based on Textures and Map Data
def draw_map():
    canvas.delete("all")
    for row in range(len(map_data)):
        for col in range(len(map_data[row])):
            tile_id = map_data[row][col]
            image = tile_images[tile_id]

            x = col * TILE_SIZE
            y = row * TILE_SIZE

            canvas.create_image(x, y, anchor="nw", image=image)

#Draw Map
draw_map()

#Main Loop
root.mainloop()