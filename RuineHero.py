#Imports
import tkinter as tk
from Maps import basic_map , fountain_map , MAPS
from playsound3 import playsound
import threading
import random
from EnemySpawns import ENEMY_SPAWNS

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
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT + 45}")
root.resizable(False, False)

#Canvas Setup
canvas = tk.Canvas(
    root,
    width=WINDOW_WIDTH,
    height=WINDOW_HEIGHT,
    bg="black",
    highlightthickness=0
)
canvas.pack()

#Mapping Tiles
map_data = basic_map
current_map_name = "basic_map"

#Map Connections
MAP_CONNECTIONS = {
    "basic_map": {
        "right": "fountain_map",
        "left": None
    },
    "fountain_map": {
        "right": None,
        "left": "basic_map"
    }
}

#Function to Transition Between Maps
def transition_to_map(new_map_name, direction):
    global map_data, current_map_name
    global player_pixel_x, player_pixel_y, target_pixel_x, target_pixel_y
    global is_moving, projectiles
    
    #Check if map exists
    if new_map_name not in MAPS:
        print(f"Error: Map '{new_map_name}' not found!")
        return
    
    print(f"Transitioning to {new_map_name} from {direction}...")
    
    #Clear all projectiles
    for projectile in projectiles:
        canvas.delete(projectile['sprite'])
    projectiles.clear()
    
    #Clear all enemies
    enemy_manager.clear_all()
    
    #Load new map
    map_data = MAPS[new_map_name]
    current_map_name = new_map_name
    
    #Set player position based on direction of entry
    current_grid_y = player_pixel_y // TILE_SIZE  # Keep same Y position
    
    if direction == "right":
        #Coming from the left, spawn on leftmost side
        player_pixel_x = 1 * TILE_SIZE  # Column 1
    elif direction == "left":
        #Coming from the right, spawn on rightmost side
        player_pixel_x = (COLS - 2) * TILE_SIZE  # Column 23
    
    player_pixel_y = current_grid_y * TILE_SIZE
    
    #Make sure spawn position is valid (not in water/trees)
    spawn_grid_x = player_pixel_x // TILE_SIZE
    spawn_grid_y = player_pixel_y // TILE_SIZE
    spawn_tile = map_data[spawn_grid_y][spawn_grid_x]
    
    #If spawn tile is not walkable, find nearest walkable tile
    if spawn_tile in NON_WALKABLE_TILES:
        #Try moving down until we find walkable ground
        for y_offset in range(ROWS):
            test_y = (spawn_grid_y + y_offset) % ROWS
            test_tile = map_data[test_y][spawn_grid_x]
            if test_tile not in NON_WALKABLE_TILES:
                player_pixel_y = test_y * TILE_SIZE
                break
    
    target_pixel_x = player_pixel_x
    target_pixel_y = player_pixel_y
    is_moving = False
    
    #Redraw everything
    draw_map()
    draw_player()
    
    #Load enemies for new map
    enemy_manager.load_enemies_for_map(new_map_name)
    
    update_stats_display()
    
    print(f"Transition complete! Now in '{new_map_name}'")


#Corresponding Tile to ID
tile_images = {
    0: tk.PhotoImage(file="TexturePack/Basic Tiles/Grass.png"),
    1: tk.PhotoImage(file="TexturePack/Basic Tiles/Water.png"),
    2: tk.PhotoImage(file="TexturePack/Basic Tiles/Stone.png"),
    3: tk.PhotoImage(file="TexturePack/Ores/Diamond.png"),
    4: tk.PhotoImage(file="TexturePack/Ores/Gold.png"),
    5: tk.PhotoImage(file="TexturePack/Ores/Ruby.png"),
    6: tk.PhotoImage(file="TexturePack/Basic Tiles/Sand.png"),
    7: tk.PhotoImage(file="TexturePack/Basic Tiles/Bush.png"),
    8: tk.PhotoImage(file="TexturePack/Basic Tiles/Apple_Tree.png"),
    9: tk.PhotoImage(file="TexturePack/Basic Tiles/Orange_Tree.png")
}

#Tile Sound Mapping
tile_sounds = {
    0: "SoundEffects/GrassWalkSFX.mp3",
    2: "SoundEffects/StoneWalkSFX.mp3",
    6: "SoundEffects/SandWalkSFX.mp3"
}

#Load Images
player_image = tk.PhotoImage(file="TexturePack/Hero/Hero.png")
enemy_image = tk.PhotoImage(file="TexturePack/Enemies/Ghost_GIF.gif")
money_image = tk.PhotoImage(file="TexturePack/Shootable/Money.png")
ninja_image = tk.PhotoImage(file="TexturePack/Enemies/Ninja.png")

#Player Stats
player_pixel_x = 5 * TILE_SIZE
player_pixel_y = 10 * TILE_SIZE
target_pixel_x = player_pixel_x
target_pixel_y = player_pixel_y
player_sprite = None
player_facing = "right"
player_max_health = 100
player_current_health = 100

#Projectile System
projectiles = []
projectile_speed = 12

#Movement settings
is_moving = False
move_speed = 8


# ==================== ENEMY CLASS ====================
class Enemy:
    
    #Initialize Enemy
    def __init__(self, x, y, enemy_type="ghost", max_health=50):
       
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        self.enemy_type = enemy_type
        self.max_health = max_health
        self.current_health = max_health
        self.alive = True
        self.sprite = None
        
        #Movement properties
        self.movement_pattern = "vertical"  #vertical, horizontal, chase, stationary, random
        self.moving_up = True
        self.moving_right = True
        self.move_timer = 0
        self.move_delay = 30  #Frames between moves
        self.move_range = 2  #How many tiles to move
        
        #Store initial position for patrol
        self.start_pixel_x = self.pixel_x
        self.start_pixel_y = self.pixel_y
        self.min_y = self.pixel_y - (self.move_range * TILE_SIZE)
        self.max_y = self.pixel_y
        self.min_x = self.pixel_x
        self.max_x = self.pixel_x + (self.move_range * TILE_SIZE)
        
        #Get enemy image based on type
        if self.enemy_type == "ninja":
            self.image = ninja_image
        elif self.enemy_type == "ghost":
            self.image = enemy_image
        else:
            self.image = enemy_image
        
        #Create sprite
        self.draw()
    
    def draw(self):
        #Draw Enemy on Canvas
        if self.sprite:
            canvas.delete(self.sprite)
        
        if self.alive:
            self.sprite = canvas.create_image(
                self.pixel_x,
                self.pixel_y,
                anchor="nw",
                image=self.image
            )
    
    def update(self):
        #Update enemy behaviour each frame
        if not self.alive:
            return
        
        #Update movement based on pattern
        if self.movement_pattern == "vertical":
            self.move_vertical()
        elif self.movement_pattern == "horizontal":
            self.move_horizontal()
        elif self.movement_pattern == "chase":
            self.chase_player()
        elif self.movement_pattern == "random":
            self.move_random()
        elif self.movement_pattern == "stationary":
            pass  #Don't move
        
        #Redraw
        self.draw()
    
    def move_vertical(self):
        #Patrol up and down
        self.move_timer += 1
        
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            
            if self.moving_up:
                new_y = self.pixel_y - TILE_SIZE
                if new_y >= self.min_y and self.can_move_to(self.pixel_x, new_y):
                    self.pixel_y = new_y
                else:
                    self.moving_up = False
            else:
                new_y = self.pixel_y + TILE_SIZE
                if new_y <= self.max_y and self.can_move_to(self.pixel_x, new_y):
                    self.pixel_y = new_y
                else:
                    self.moving_up = True
    
    def move_horizontal(self):
        #Patrol left and right
        self.move_timer += 1
        
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            
            if self.moving_right:
                new_x = self.pixel_x + TILE_SIZE
                if new_x <= self.max_x and self.can_move_to(new_x, self.pixel_y):
                    self.pixel_x = new_x
                else:
                    self.moving_right = False
            else:
                new_x = self.pixel_x - TILE_SIZE
                if new_x >= self.min_x and self.can_move_to(new_x, self.pixel_y):
                    self.pixel_x = new_x
                else:
                    self.moving_right = True
    
    def chase_player(self):
        #Chase the player (simple AI)
        self.move_timer += 1
        
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            
            #Calculate direction to player
            dx = player_pixel_x - self.pixel_x
            dy = player_pixel_y - self.pixel_y
            
            #Move towards player (one axis at a time)
            if abs(dx) > abs(dy):
                #Move horizontally
                if dx > 0:
                    new_x = self.pixel_x + TILE_SIZE
                    if self.can_move_to(new_x, self.pixel_y):
                        self.pixel_x = new_x
                else:
                    new_x = self.pixel_x - TILE_SIZE
                    if self.can_move_to(new_x, self.pixel_y):
                        self.pixel_x = new_x
            else:
                #Move vertically
                if dy > 0:
                    new_y = self.pixel_y + TILE_SIZE
                    if self.can_move_to(self.pixel_x, new_y):
                        self.pixel_y = new_y
                else:
                    new_y = self.pixel_y - TILE_SIZE
                    if self.can_move_to(self.pixel_x, new_y):
                        self.pixel_y = new_y
    
    def move_random(self):
        #Move in random directions
        self.move_timer += 1
        
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            
            #Choose random direction
            direction = random.choice(['up', 'down', 'left', 'right'])
            
            if direction == 'up':
                new_pos = (self.pixel_x, self.pixel_y - TILE_SIZE)
            elif direction == 'down':
                new_pos = (self.pixel_x, self.pixel_y + TILE_SIZE)
            elif direction == 'left':
                new_pos = (self.pixel_x - TILE_SIZE, self.pixel_y)
            else:  #right
                new_pos = (self.pixel_x + TILE_SIZE, self.pixel_y)
            
            if self.can_move_to(new_pos[0], new_pos[1]):
                self.pixel_x = new_pos[0]
                self.pixel_y = new_pos[1]
    
    def can_move_to(self, pixel_x, pixel_y):
        #Check if enemy can move to specified pixel position/ Tile
        grid_x = pixel_x // TILE_SIZE
        grid_y = pixel_y // TILE_SIZE
        
        #Check boundaries
        if not (0 <= grid_x < COLS and 0 <= grid_y < ROWS):
            return False
        
        #Check if tile is walkable
        tile_id = map_data[grid_y][grid_x]
        if tile_id in NON_WALKABLE_TILES:
            return False
        
        return True
    
    def take_damage(self, damage):
        #Enemy Takes Damage
        if not self.alive:
            return
        
        self.current_health -= damage
        print(f"Enemy hit! Health: {self.current_health}/{self.max_health}")
        
        if self.current_health <= 0:
            self.die()
    
    def die(self):
        #Enemy Death Handling
        self.alive = False
        if self.sprite:
            canvas.delete(self.sprite)
        print(f"Enemy defeated at ({self.grid_x}, {self.grid_y})!")
    
    def get_bounds(self):
        #Return enemy bounding box for collision detection
        return {
            'left': self.pixel_x,
            'right': self.pixel_x + TILE_SIZE,
            'top': self.pixel_y,
            'bottom': self.pixel_y + TILE_SIZE
        }


# ==================== ENEMY MANAGER ====================
class EnemyManager:
    #Manages All Enemies in the Game
    
    def __init__(self):
        self.enemies = []
    
    #Function to Add New Enemy To the Game
    def add_enemy(self, x, y, enemy_type="ghost", max_health=50, movement_pattern="vertical", move_range=2):
        enemy = Enemy(x, y, enemy_type, max_health)
        enemy.movement_pattern = movement_pattern
        enemy.move_range = move_range
        
        #Recalculate patrol bounds based on move_range
        enemy.min_y = enemy.start_pixel_y - (move_range * TILE_SIZE)
        enemy.max_y = enemy.start_pixel_y
        enemy.min_x = enemy.start_pixel_x
        enemy.max_x = enemy.start_pixel_x + (move_range * TILE_SIZE)
        
        self.enemies.append(enemy)
        return enemy
    
    def load_enemies_for_map(self, map_name):
        
        #Clear any existing enemies first
        self.clear_all()
        
        #Get enemy spawn data for this map
        if map_name not in ENEMY_SPAWNS:
            print(f"No enemy spawns defined for map: {map_name}")
            return
        
        enemy_data_list = ENEMY_SPAWNS[map_name]
        
        #Spawn each enemy
        for enemy_data in enemy_data_list:
            new_enemy = self.add_enemy(
                x=enemy_data["x"],
                y=enemy_data["y"],
                enemy_type=enemy_data.get("type", "ghost"),
                max_health=enemy_data.get("health", 50),
                movement_pattern=enemy_data.get("pattern", "vertical"),
                move_range=enemy_data.get("move_range", 2)
            )
            
            #Set custom move delay if specified
            if "move_delay" in enemy_data:
                new_enemy.move_delay = enemy_data["move_delay"]
        
        print(f"Loaded {len(enemy_data_list)} enemies for {map_name}")
    
    def update_all(self):
        #Update all enemies
        for enemy in self.enemies:
            enemy.update()
    
    def remove_dead_enemies(self):
        #Remove dead enemies from the list
        self.enemies = [enemy for enemy in self.enemies if enemy.alive]
    
    def get_living_enemies(self):
        #Return list of living enemies
        return [enemy for enemy in self.enemies if enemy.alive]
    
    def clear_all(self):
        #Clear all enemies from the game
        for enemy in self.enemies:
            if enemy.sprite:
                canvas.delete(enemy.sprite)
        self.enemies.clear()


#Create enemy manager
enemy_manager = EnemyManager()

#Stats Panel Setup
stats_frame = tk.Frame(root, bg="#2b2b2b", height=100)
stats_frame.pack(fill=tk.X)

#Stats Labels
player_health_label = tk.Label(
    stats_frame,
    text=f"Health: {player_current_health}/{player_max_health}",
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

enemy_count_label = tk.Label(
    stats_frame,
    text=f"Enemies: {len(enemy_manager.get_living_enemies())}",
    font=("Arial", 12),
    bg="#2b2b2b",
    fg="#ffaa44"
)
enemy_count_label.pack(side=tk.LEFT, padx=20, pady=10)


def update_stats_display():
    player_health_label.config(text=f"Health: {player_current_health}/{player_max_health}")
    player_money_label.config(text=f"Money: ${player_money}")
    player_facing_label.config(text=f"Facing: {player_facing.upper()}")
    enemy_count_label.config(text=f"Enemies: {len(enemy_manager.get_living_enemies())}")


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

#Function to Check Projectile Collision with Enemy
def check_projectile_enemy_collision():
    global projectiles
    
    projectiles_to_remove = []
    
    #Get Projectile Positions
    for projectile in projectiles:
        proj_x = projectile['x']
        proj_y = projectile['y']
        
        #Check collision with all living enemies
        for enemy in enemy_manager.get_living_enemies():
            bounds = enemy.get_bounds()
            
            if (bounds['left'] < proj_x < bounds['right'] and
                bounds['top'] < proj_y < bounds['bottom']):
                
                #Hit!
                enemy.take_damage(10)
                
                #Remove projectile
                canvas.delete(projectile['sprite'])
                projectiles_to_remove.append(projectile)
                break  # Stop checking other enemies for this projectile
    
    #Remove hit projectiles
    for projectile in projectiles_to_remove:
        if projectile in projectiles:
            projectiles.remove(projectile)
    
    # Clean up dead enemies
    enemy_manager.remove_dead_enemies()
    update_stats_display()


#Function to get tile ID at position
def get_tile_id_at_position(pixel_x, pixel_y):
    grid_x = pixel_x // TILE_SIZE
    grid_y = pixel_y // TILE_SIZE

    if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
        return map_data[grid_y][grid_x]
    return 0


#Function to get sound for current tile
def get_sound_for_tile(tile_id):
    return tile_sounds.get(tile_id, "SoundEffects/GrassWalkSFX.mp3")


#Function to play SFX
def play_sfx(sound_file):
    global is_sound_playing
    
    #Dont play if sound is already playing
    if is_sound_playing:
        return
    
    def play_in_thread():
        global is_sound_playing
        is_sound_playing = True
        playsound(sound_file)
        is_sound_playing = False
    
    thread = threading.Thread(target=play_in_thread, daemon=True)
    thread.start()

#Function to play Money SFX
def play_money_sfx():
    def play_in_thread():
        playsound("SoundEffects/MoneySFX.mp3")
    
    thread = threading.Thread(target=play_in_thread, daemon=True)
    thread.start()

#Function to Shoot Money Projectile
def shoot_money():
    global player_money

    #Check if enough money
    if player_money < 100:
        print("Not enough money to shoot!")
        return
    
    #Deduct Money
    player_money -= 100
    print(f"Shot money! Remaining: ${player_money}")
    update_stats_display()
    play_money_sfx()

    #Calculate Starting Position and Direction
    start_x = player_pixel_x + TILE_SIZE // 2
    start_y = player_pixel_y + TILE_SIZE // 2
    
    #Determine Direction Based on Facing
    if player_facing == "up":
        dx, dy = 0, -1
    elif player_facing == "down":
        dx, dy = 0, 1
    elif player_facing == "left":
        dx, dy = -1, 0
    elif player_facing == "right":
        dx, dy = 1, 0
    else:
        dx, dy = 1, 0
    
    #Create Projectile Sprite
    projectile_sprite = canvas.create_image(
        start_x,
        start_y,
        image=money_image
    )
    
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
        projectile['x'] += projectile['dx'] * projectile_speed
        projectile['y'] += projectile['dy'] * projectile_speed
        
        canvas.coords(
            projectile['sprite'],
            projectile['x'],
            projectile['y']
        )
        
        if (projectile['x'] < 0 or projectile['x'] > WINDOW_WIDTH or
            projectile['y'] < 0 or projectile['y'] > WINDOW_HEIGHT):
            projectiles_to_remove.append(projectile)
    
    for projectile in projectiles_to_remove:
        canvas.delete(projectile['sprite'])
        projectiles.remove(projectile)


#Function to Update Player Animation
def update_player():
    global player_pixel_x, player_pixel_y, is_moving
    
    if is_moving:
        if player_pixel_x < target_pixel_x:
            player_pixel_x += move_speed
            if player_pixel_x > target_pixel_x:
                player_pixel_x = target_pixel_x
        elif player_pixel_x > target_pixel_x:
            player_pixel_x -= move_speed
            if player_pixel_x < target_pixel_x:
                player_pixel_x = target_pixel_x
        
        if player_pixel_y < target_pixel_y:
            player_pixel_y += move_speed
            if player_pixel_y > target_pixel_y:
                player_pixel_y = target_pixel_y
        elif player_pixel_y > target_pixel_y:
            player_pixel_y -= move_speed
            if player_pixel_y < target_pixel_y:
                player_pixel_y = target_pixel_y
        
        if player_pixel_x == target_pixel_x and player_pixel_y == target_pixel_y:
            is_moving = False
        
        draw_player()
    
    # Update all enemies
    enemy_manager.update_all()
    
    # Update projectiles
    update_projectiles()
    
    # Check collisions
    check_projectile_enemy_collision()
    
    # Schedule next frame
    root.after(16, update_player)


#Function to Move Player
def move_player(dx, dy):
    global target_pixel_x, target_pixel_y, is_moving, move_speed, player_facing
    
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

    #Check if trying to move beyond RIGHT edge
    if new_grid_x >= COLS:
        if current_map_name in MAP_CONNECTIONS:
            next_map = MAP_CONNECTIONS[current_map_name].get("right")
            if next_map:
                transition_to_map(next_map, "right")
                return
        return  # Block movement if no map connection
    
    #Check if trying to move beyond LEFT edge
    if new_grid_x < 0:
        if current_map_name in MAP_CONNECTIONS:
            next_map = MAP_CONNECTIONS[current_map_name].get("left")
            if next_map:
                transition_to_map(next_map, "left")
                return
        return  # Block movement if no map connection

    #Check other boundaries (top/bottom)
    if not (0 <= new_grid_y < ROWS):
        return

    #Get the tile we're about to walk onto
    target_tile_id = map_data[new_grid_y][new_grid_x]

    #Collision Detection for Non-Walkable Tiles
    if target_tile_id in NON_WALKABLE_TILES:
        return
    
    #Adjust speed based on tile
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
    
    #Play Tile Specific Sound
    play_sfx(sound_file)


#Function to Handle Key Press and Movement Events
def on_key_press(event):
    key = event.keysym.lower()
    
    # Movement Controls
    if key == 'w' or key == 'up':
        move_player(0, -1)
    elif key == 's' or key == 'down':
        move_player(0, 1)
    elif key == 'a' or key == 'left':
        move_player(-1, 0)
    elif key == 'd' or key == 'right':
        move_player(1, 0)
    #Shoot Money Controls
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

#Load Enemies From Configuration
#Enemies for the basic_map from EnemySpawns.py
enemy_manager.load_enemies_for_map("basic_map")

# Draw Map
draw_map()
draw_player()
update_stats_display()

# Start the animation loop
update_player()

# Main Loop
root.mainloop()