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

player_image = tk.PhotoImage(file = "TexturePack/Hero/Hero.png")
player_x= 5
player_y= 5
player_sprite = None

#Function to Draw Player
def draw_player():
    global player_sprite
    if player_sprite:
        canvas.delete(player_sprite)
        
    # Draw player at current position
    px = player_x * TILE_SIZE
    py = player_y * TILE_SIZE
    player_sprite = canvas.create_image(px, py, anchor="nw", image=player_image)

#Function to Move Player
def move_player(dx, dy):
    global player_x , player_y
    new_x = player_x + dx
    new_y = player_y + dy

    # Check boundaries
    if 0 <= new_x < COLS and 0 <= new_y < ROWS:
        player_x = new_x
        player_y = new_y
        draw_player()

#Function to Handle Key Press and Movement Events
def on_key_press(event):
    key = event.keysym.lower()
    
    # WASD and Arrow key controls
    if key == 'w' or key == 'up':
        move_player(0, -1)  # Move up
    elif key == 's' or key == 'down':
        move_player(0, 1)   # Move down
    elif key == 'a' or key == 'left':
        move_player(-1, 0)  # Move left
    elif key == 'd' or key == 'right':
        move_player(1, 0)   # Move right

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

# Bind keyboard input
root.bind("<KeyPress>", on_key_press)

#Draw Map
draw_map()
draw_player()

#Main Loop
root.mainloop()