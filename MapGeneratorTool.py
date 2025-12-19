import tkinter as tk
from tkinter import messagebox, filedialog

# Window and Tile Configuration
TILE_SIZE = 32
COLS = 25
ROWS = 21

WINDOW_WIDTH = COLS * TILE_SIZE  # 800
WINDOW_HEIGHT = ROWS * TILE_SIZE  # 672

# Main Window
root = tk.Tk()
root.title("Ruine Hero - Map Editor")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT + 100}")
root.resizable(False, False)
root.configure(bg="#2b2b2b")

# Canvas Setup
canvas = tk.Canvas(
    root,
    width=WINDOW_WIDTH,
    height=WINDOW_HEIGHT,
    bg="black",
    highlightthickness=0
)
canvas.pack()

# Initialize Empty Map
map_data = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Tile Images
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

# Tile Names for Display
tile_names = {
    0: "Grass",
    1: "Water",
    2: "Stone",
    3: "Diamond",
    4: "Gold",
    5: "Ruby",
    6: "Sand",
    7: "Bush",
    8: "Apple Tree",
    9: "Orange Tree"
}

# Current Selected Tile
current_tile = 0

# Draw Map Function
def draw_map():
    canvas.delete("all")
    for row in range(len(map_data)):
        for col in range(len(map_data[row])):
            tile_id = map_data[row][col]
            image = tile_images[tile_id]
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            canvas.create_image(x, y, anchor="nw", image=image)
    
    # Draw grid overlay
    for x in range(0, WINDOW_WIDTH, TILE_SIZE):
        canvas.create_line(x, 0, x, WINDOW_HEIGHT, fill="#333", width=1)
    for y in range(0, WINDOW_HEIGHT, TILE_SIZE):
        canvas.create_line(0, y, WINDOW_WIDTH, y, fill="#333", width=1)

# Change Tile on Click
def change_tile(event):
    col = event.x // TILE_SIZE
    row = event.y // TILE_SIZE
    
    if 0 <= row < ROWS and 0 <= col < COLS:
        map_data[row][col] = current_tile
        draw_map()

# Select Tile with Number Keys
def select_tile(num):
    global current_tile
    if num in tile_images:
        current_tile = num
        update_status()

# Save Map to File
def save_map():
    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        title="Save Map"
    )
    if filename:
        with open(filename, "w") as f:
            f.write("map_data = [\n")
            for row in map_data:
                f.write(f"    {row},\n")
            f.write("]\n")
        messagebox.showinfo("Success", f"Map saved to {filename}!")

# Load Map from File
def load_map():
    filename = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        title="Load Map"
    )
    if filename:
        try:
            with open(filename, "r") as f:
                content = f.read()
                # Execute the file content to get map_data
                local_vars = {}
                exec(content, {}, local_vars)
                loaded_map = local_vars.get("map_data", [])
                
                # Validate and resize if necessary
                if loaded_map:
                    global map_data
                    map_data = [[0 for _ in range(COLS)] for _ in range(ROWS)]
                    for row in range(min(len(loaded_map), ROWS)):
                        for col in range(min(len(loaded_map[row]), COLS)):
                            map_data[row][col] = loaded_map[row][col]
                    draw_map()
                    messagebox.showinfo("Success", "Map loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load map: {e}")

# Clear Map
def clear_map():
    global map_data
    if messagebox.askyesno("Clear Map", "Are you sure you want to clear the entire map?"):
        map_data = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        draw_map()

# Fill Map with Current Tile
def fill_map():
    global map_data
    if messagebox.askyesno("Fill Map", f"Fill entire map with {tile_names[current_tile]}?"):
        map_data = [[current_tile for _ in range(COLS)] for _ in range(ROWS)]
        draw_map()

# Update Status Label
def update_status():
    status_label.config(text=f"Selected Tile: {tile_names[current_tile]} (Press {current_tile})")

# Key Press Handler
def key_pressed(event):
    if event.char.lower() == 's':
        save_map()
    elif event.char.lower() == 'l':
        load_map()
    elif event.char.lower() == 'c':
        clear_map()
    elif event.char.lower() == 'f':
        fill_map()
    else:
        try:
            num = int(event.char)
            select_tile(num)
        except:
            pass

# Mouse Bindings
canvas.bind("<Button-1>", change_tile)
canvas.bind("<B1-Motion>", change_tile)

# Keyboard Bindings
root.bind("<Key>", key_pressed)

# UI Panel
ui_frame = tk.Frame(root, bg="#2b2b2b", height=100)
ui_frame.pack(fill=tk.X)

# Status Label
status_label = tk.Label(
    ui_frame,
    text=f"Selected Tile: {tile_names[current_tile]} (Press {current_tile})",
    font=("Arial", 12, "bold"),
    bg="#2b2b2b",
    fg="white"
)
status_label.pack(pady=5)

# Tile Selection Buttons
button_frame = tk.Frame(ui_frame, bg="#2b2b2b")
button_frame.pack(pady=5)

for tile_id in range(6):
    btn = tk.Button(
        button_frame,
        text=f"{tile_id}: {tile_names[tile_id]}",
        command=lambda t=tile_id: select_tile(t),
        width=12,
        bg="#444",
        fg="white",
        font=("Arial", 9)
    )
    btn.pack(side=tk.LEFT, padx=2)

# Action Buttons
action_frame = tk.Frame(ui_frame, bg="#2b2b2b")
action_frame.pack(pady=5)

save_btn = tk.Button(action_frame, text="Save (S)", command=save_map, width=10, bg="#4CAF50", fg="white")
save_btn.pack(side=tk.LEFT, padx=5)

load_btn = tk.Button(action_frame, text="Load (L)", command=load_map, width=10, bg="#2196F3", fg="white")
load_btn.pack(side=tk.LEFT, padx=5)

clear_btn = tk.Button(action_frame, text="Clear (C)", command=clear_map, width=10, bg="#f44336", fg="white")
clear_btn.pack(side=tk.LEFT, padx=5)

fill_btn = tk.Button(action_frame, text="Fill (F)", command=fill_map, width=10, bg="#FF9800", fg="white")
fill_btn.pack(side=tk.LEFT, padx=5)

# Instructions
instructions = tk.Label(
    ui_frame,
    text="Controls: Click/Drag to paint | Press 0-5 to select tiles | S=Save | L=Load | C=Clear | F=Fill",
    font=("Arial", 9),
    bg="#2b2b2b",
    fg="#aaa"
)
instructions.pack(pady=2)

# Initial Draw
draw_map()

# Main Loop
root.mainloop()