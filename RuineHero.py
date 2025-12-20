#Imports
import tkinter as tk
from Maps import basic_map
from playsound3 import playsound
import threading

#Calculate Tile Grid and Size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 672
TILE_SIZE = 32

COLS = WINDOW_WIDTH // TILE_SIZE
ROWS = WINDOW_HEIGHT // TILE_SIZE

#Check if sound is playing
is_sound_playing = False

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
    6: tk.PhotoImage(file = "TexturePack/Basic Tiles/Sand.png"),
    7: tk.PhotoImage(file = "TexturePack/Basic Tiles/Bush.png"),
    8: tk.PhotoImage(file = "TexturePack/Basic Tiles/Apple_Tree.png"),
    9: tk.PhotoImage(file = "TexturePack/Basic Tiles/Orange_Tree.png")
}

player_image = tk.PhotoImage(file = "TexturePack/Hero/Hero.png")
enemy_image = tk.PhotoImage(file = "TexturePack/Enemies/Ghost_GIF.gif")

# Player position - now in PIXELS instead of grid
player_pixel_x = 5 * TILE_SIZE  # Start at grid (5, 5) = pixel (160, 160)
player_pixel_y = 10 * TILE_SIZE
target_pixel_x = player_pixel_x  # Where we're moving TO
target_pixel_y = player_pixel_y
player_sprite = None

#Enemy Positioning and Image
enemy_sprite = None
enemy_pixel_x = 15 * TILE_SIZE
enemy_pixel_y = 10 * TILE_SIZE

#Function to Draw Enemy
def draw_enemy():
    global enemy_sprite
    if enemy_sprite:
        canvas.delete(enemy_sprite)

    enemy_sprite = canvas.create_image(
        enemy_pixel_x,
        enemy_pixel_y,
        anchor="nw",
        image=enemy_image
    )

# Movement settings
is_moving = False  # Is the player currently animating?
move_speed = 8  # Pixels per frame (32/8 = 4 frames to cross one tile)

#Function to Draw Player
def draw_player():
    global player_sprite
    if player_sprite:
        canvas.delete(player_sprite)
    
    # Draw player at current pixel position (not grid position!)
    player_sprite = canvas.create_image(
        player_pixel_x, 
        player_pixel_y, 
        anchor="nw", 
        image=player_image
    )

#Function to play SFX 
def play_sfx(sound_file):
    global is_sound_playing
    
    # Don't play if already playing
    if is_sound_playing:
        return
    
    def play_in_thread():
        global is_sound_playing
        is_sound_playing = True
        playsound(sound_file)
        is_sound_playing = False  # Mark as finished
    
    thread = threading.Thread(target=play_in_thread, daemon=True)
    thread.start()

#Function to Update Player Animation
def update_player():
    global player_pixel_x, player_pixel_y, is_moving
    
    if is_moving:

        # Move horizontally toward target
        if player_pixel_x < target_pixel_x:
            player_pixel_x += move_speed  # Move right
            if player_pixel_x > target_pixel_x:  # Don't overshoot
                player_pixel_x = target_pixel_x
        elif player_pixel_x > target_pixel_x:
            player_pixel_x -= move_speed  # Move left
            if player_pixel_x < target_pixel_x:  # Don't overshoot
                player_pixel_x = target_pixel_x
        
        # Move vertically toward target
        if player_pixel_y < target_pixel_y:
            player_pixel_y += move_speed  # Move down
            if player_pixel_y > target_pixel_y:  # Don't overshoot
                player_pixel_y = target_pixel_y
        elif player_pixel_y > target_pixel_y:
            player_pixel_y -= move_speed  # Move up
            if player_pixel_y < target_pixel_y:  # Don't overshoot
                player_pixel_y = target_pixel_y
        
        # Check if we've reached the target
        if player_pixel_x == target_pixel_x and player_pixel_y == target_pixel_y:
            is_moving = False  # Stop animating
        
        # Redraw player at new position
        draw_player()
        draw_enemy()
    
    # Schedule next frame (~60 FPS = every 16 milliseconds)
    root.after(16, update_player)

#Function to Move Player
def move_player(dx, dy):
    global target_pixel_x, target_pixel_y, is_moving
    
    # Don't allow new movement if already moving
    if is_moving:
        return
    
    # Calculate current grid position
    current_grid_x = player_pixel_x // TILE_SIZE
    current_grid_y = player_pixel_y // TILE_SIZE
    
    # Calculate new grid position
    new_grid_x = current_grid_x + dx
    new_grid_y = current_grid_y + dy
    
    # Check boundaries
    if 0 <= new_grid_x < COLS and 0 <= new_grid_y < ROWS:
        # Set the target position in pixels
        target_pixel_x = new_grid_x * TILE_SIZE
        target_pixel_y = new_grid_y * TILE_SIZE
        is_moving = True  # Start the animation
        play_sfx("SoundEffects/GrassWalkSFX.mp3") 
        
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
draw_enemy()

# Start the animation loop
update_player()

#Main Loop
root.mainloop()