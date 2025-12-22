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

#Non Walking Tiles
NON_WALKABLE_TILES = [1, 8, 9]

#Money Counter
player_money = 5000

#Main Window
root = tk.Tk()
root.title("Ruine Hero")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT + 45}") #Extra space for stats panel
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

#Tile Sound Mapping - Maps tile ID to sound file
tile_sounds = {
    0: "SoundEffects/GrassWalkSFX.mp3",
    2: "SoundEffects/StoneWalkSFX.mp3",
    6: "SoundEffects/SandWalkSFX.mp3"
}

#Load Images
player_image = tk.PhotoImage(file = "TexturePack/Hero/Hero.png")
enemy_image = tk.PhotoImage(file = "TexturePack/Enemies/Ghost_GIF.gif")
money_image = tk.PhotoImage(file = "TexturePack/Shootable/Money.png")

# Player Stats
player_pixel_x = 5 * TILE_SIZE
player_pixel_y = 10 * TILE_SIZE
target_pixel_x = player_pixel_x
target_pixel_y = player_pixel_y
player_sprite = None
player_facing = "right"  # Track which direction player is facing
player_max_health = 100
player_current_health = 100

#Enemy Stats
enemy_sprite = None
enemy_pixel_x = 15 * TILE_SIZE
enemy_pixel_y = 11 * TILE_SIZE
enemy_max_health = 50
enemy_current_health = 50
enemy_alive = True

#Enemy Movement Variables
enemy_moving_up = True
enemy_move_timer = 0
enemy_move_delay = 30 
enemy_min_y = enemy_pixel_y - (2 * TILE_SIZE)  
enemy_max_y = enemy_pixel_y 

# Projectile System
projectiles = []  # List to store all active projectiles
projectile_speed = 12  # Pixels per frame (faster than player)

# Movement settings
is_moving = False
move_speed = 8

#Stats Panel Setup (AFTER defining player stats variables!)
stats_frame = tk.Frame(root, bg="#2b2b2b", height=100)
stats_frame.pack(fill=tk.X)

#Stats Labels
player_health_label = tk.Label(
    stats_frame,
    text=f"Health: {player_current_health}/{player_max_health}",  # ✅ Fixed missing comma
    font=("Arial", 14, "bold"),
    bg="#2b2b2b",
    fg="#ff4444"
)
player_health_label.pack(side=tk.LEFT, padx=20, pady=10)

player_money_label = tk.Label(
    stats_frame,
    text=f"Money: ${player_money}",
    font=("Arial", 14, "bold"),
    bg="#2b2b2b",
    fg="#44ff44"
)
player_money_label.pack(side=tk.LEFT, padx=20, pady=10)

player_facing_label = tk.Label(
    stats_frame,
    text=f"Facing: {player_facing.upper()}",
    font=("Arial", 12),
    bg="#2b2b2b",
    fg="#ffffff"
)
player_facing_label.pack(side=tk.LEFT, padx=20, pady=10)

def update_stats_display():
    player_health_label.config(text=f"Health: {player_current_health}/{player_max_health}")
    player_money_label.config(text=f"Money: ${player_money}")
    player_facing_label.config(text=f"Facing: {player_facing.upper()}")

#Function to Draw Player
def draw_player():
    global player_sprite
    if player_sprite:
        canvas.delete(player_sprite)
    
    player_sprite = canvas.create_image(
        player_pixel_x, 
        player_pixel_y, 
        anchor="nw", 
        image=player_image
    )

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

#Function to Update Enemy Movement
def update_enemy_movement():
    global enemy_pixel_y, enemy_moving_up, enemy_move_timer
    
    if not enemy_alive:
        return

    # Increment timer
    enemy_move_timer += 1
    
    # Check if it's time to move
    if enemy_move_timer >= enemy_move_delay:
        enemy_move_timer = 0  # Reset timer
        
        # Move enemy
        if enemy_moving_up:
            enemy_pixel_y -= TILE_SIZE
            
            # Check if reached upper limit
            if enemy_pixel_y <= enemy_min_y:
                enemy_moving_up = False 
        else:
            enemy_pixel_y += TILE_SIZE
            
            # Check if reached lower limit
            if enemy_pixel_y >= enemy_max_y:
                enemy_moving_up = True  # Turn around
        
        # Redraw enemy at new position
        draw_enemy()

#Function to Check Projectile Collision with Enemy
def check_projectile_enemy_collision():
    global enemy_current_health, projectiles, enemy_alive
    
    if not enemy_alive:
        return

    projectiles_to_remove = []
    
    for projectile in projectiles:
        # Get projectile position
        proj_x = projectile['x']
        proj_y = projectile['y']
        
        # Check if projectile overlaps with enemy (simple box collision)
        # Enemy is 32x32 pixels at (enemy_pixel_x, enemy_pixel_y)
        if (enemy_pixel_x < proj_x < enemy_pixel_x + TILE_SIZE and
            enemy_pixel_y < proj_y < enemy_pixel_y + TILE_SIZE):
            
            # HIT! Deal damage to enemy
            enemy_current_health -= 10
            if enemy_current_health <= 0:
                enemy_alive = False
                
            print(f"Enemy hit! Health: {enemy_current_health}/{enemy_max_health}")
            
            # Remove the projectile
            canvas.delete(projectile['sprite'])
            projectiles_to_remove.append(projectile)
            
            # Check if enemy is dead
            if enemy_current_health <= 0:
                print("Enemy defeated!")
                canvas.delete(enemy_sprite)
                # Later: remove enemy, drop loot, etc.
    
    # Remove hit projectiles
    for projectile in projectiles_to_remove:
        if projectile in projectiles:
            projectiles.remove(projectile)

#Function to get tile ID at position
def get_tile_id_at_position(pixel_x, pixel_y):
    grid_x = pixel_x // TILE_SIZE
    grid_y = pixel_y // TILE_SIZE

        # Check if position is within bounds
    if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
        return map_data[grid_y][grid_x]
    return 0

#Function to get sound for current tile
def get_sound_for_tile(tile_id):
     return tile_sounds.get(tile_id, "SoundEffects/GrassWalkSFX.mp3")

#Function to play SFX 
def play_sfx(sound_file):
    global is_sound_playing
    
    #Dont play if already playing
    if is_sound_playing:
        return
    
    def play_in_thread():
        global is_sound_playing
        is_sound_playing = True
        playsound(sound_file)
        is_sound_playing = False
    
    thread = threading.Thread(target=play_in_thread, daemon=True)
    thread.start()

#Fuction to play Money SFX
def play_money_sfx():
    def play_in_thread():
        playsound("SoundEffects/MoneySFX.mp3")
    
    thread = threading.Thread(target=play_in_thread, daemon=True)
    thread.start()

#Function to Shoot Money Projectile
def shoot_money():
    global player_money

    # Check if player has money
    if player_money < 100:
        print("Not enough money to shoot!")
        return
    
    # Deduct money cost
    player_money -= 100
    print(f"Shot money! Remaining: ${player_money}")
    update_stats_display()
    play_money_sfx()

    # Calculate starting position (center of player sprite)
    start_x = player_pixel_x + TILE_SIZE // 2
    start_y = player_pixel_y + TILE_SIZE // 2
    
    # Set direction based on which way player is facing
    if player_facing == "up":
        dx, dy = 0, -1
    elif player_facing == "down":
        dx, dy = 0, 1
    elif player_facing == "left":
        dx, dy = -1, 0
    elif player_facing == "right":
        dx, dy = 1, 0
    else:
        dx, dy = 1, 0  # Default to right
    
    # Create projectile sprite
    projectile_sprite = canvas.create_image(
        start_x,
        start_y,
        image=money_image
    )
    
    # Add to projectiles list
    projectile = {
        'sprite': projectile_sprite,
        'x': start_x,
        'y': start_y,
        'dx': dx,
        'dy': dy
    }
    projectiles.append(projectile)

#Function to Update Projectiles
def update_projectiles():
    global projectiles
    
    projectiles_to_remove = []
    
    for projectile in projectiles:
        # Move projectile
        projectile['x'] += projectile['dx'] * projectile_speed
        projectile['y'] += projectile['dy'] * projectile_speed
        
        # Update sprite position
        canvas.coords(
            projectile['sprite'],
            projectile['x'],
            projectile['y']
        )
        
        # Check if projectile is out of bounds
        if (projectile['x'] < 0 or projectile['x'] > WINDOW_WIDTH or
            projectile['y'] < 0 or projectile['y'] > WINDOW_HEIGHT):
            # Mark for removal
            projectiles_to_remove.append(projectile)
    
    # Remove out-of-bounds projectiles
    for projectile in projectiles_to_remove:
        canvas.delete(projectile['sprite'])
        projectiles.remove(projectile)

#Function to Update Player Animation
def update_player():
    global player_pixel_x, player_pixel_y, is_moving
    
    if is_moving:
        # Move horizontally toward target
        if player_pixel_x < target_pixel_x:
            player_pixel_x += move_speed
            if player_pixel_x > target_pixel_x:
                player_pixel_x = target_pixel_x
        elif player_pixel_x > target_pixel_x:
            player_pixel_x -= move_speed
            if player_pixel_x < target_pixel_x:
                player_pixel_x = target_pixel_x
        
        # Move vertically toward target
        if player_pixel_y < target_pixel_y:
            player_pixel_y += move_speed
            if player_pixel_y > target_pixel_y:
                player_pixel_y = target_pixel_y
        elif player_pixel_y > target_pixel_y:
            player_pixel_y -= move_speed
            if player_pixel_y < target_pixel_y:
                player_pixel_y = target_pixel_y
        
        # Check if we've reached the target
        if player_pixel_x == target_pixel_x and player_pixel_y == target_pixel_y:
            is_moving = False
        
        # Redraw sprites
        draw_player()

    if enemy_alive:
        draw_enemy()
    
    # Update projectiles every frame
    update_projectiles()
    
    #Update Enemy Movement
    update_enemy_movement()
    check_projectile_enemy_collision()
    # Schedule next frame
    root.after(16, update_player)

#Function to Move Player
def move_player(dx, dy):
    global target_pixel_x, target_pixel_y, is_moving, move_speed, player_facing
    
    # Don't allow new movement if already moving
    if is_moving:
        return
    
    # Update player facing direction
    if dy == -1:
        player_facing = "up"
    elif dy == 1:
        player_facing = "down"
    elif dx == -1:
        player_facing = "left"
    elif dx == 1:
        player_facing = "right"

    update_stats_display()
    
    current_grid_x = player_pixel_x // TILE_SIZE
    current_grid_y = player_pixel_y // TILE_SIZE
    
    #Calculate New Grid Position
    new_grid_x = current_grid_x + dx
    new_grid_y = current_grid_y + dy

    # Check boundaries
    if 0 <= new_grid_x < COLS and 0 <= new_grid_y < ROWS:
        #Get the tile we're about to walk onto
        target_tile_id = map_data[new_grid_y][new_grid_x]

        #Collision Detection for Non-Walkable Tiles
        if target_tile_id in NON_WALKABLE_TILES:
            return
        
        # Adjust speed based on tile
        if target_tile_id == 6:
            move_speed = 4
        else:
            move_speed = 8

        #Get appropriate Sound for Tile
        sound_file = get_sound_for_tile(target_tile_id)
        
        #Set Target Position in Pixels
        target_pixel_x = new_grid_x * TILE_SIZE
        target_pixel_y = new_grid_y * TILE_SIZE
        is_moving = True
        
        # Play Tile Specific Sound
        play_sfx(sound_file)

#Function to Handle Key Press and Movement Events
def on_key_press(event):
    key = event.keysym.lower()
    
    # Movement controls
    if key == 'w' or key == 'up':
        move_player(0, -1)
    elif key == 's' or key == 'down':
        move_player(0, 1)
    elif key == 'a' or key == 'left':
        move_player(-1, 0)
    elif key == 'd' or key == 'right':
        move_player(1, 0)
    
    # Shooting control
    elif key == 'space':
        shoot_money()

#Draw Map Function
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
update_stats_display()

# Start the animation loop
update_player()

#Main Loop
root.mainloop()