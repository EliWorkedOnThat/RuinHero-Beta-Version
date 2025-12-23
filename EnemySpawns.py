#This file will contain all enemy spawn locations for each level as well as
#Doordinates , Type of Enemy , Health , etc.

basic_map_enemies = [
    {"x": 15, "y": 11, "type": "ghost", "pattern": "vertical", "health": 50},
    {"x": 18, "y": 8, "type": "ghost", "pattern": "horizontal", "health": 40},
]

fountain_map_enemies = [
        {"x": 12, "y": 10, "type": "ghost", "pattern": "stationary", "health": 150},
        {"x": 8, "y": 6, "type": "ghost", "pattern": "vertical", "health": 60},
        {"x": 16, "y": 6, "type": "ghost", "pattern": "vertical", "health": 60},
        {"x": 10, "y": 15, "type": "ghost", "pattern": "horizontal", "health": 50},
]

ENEMY_SPAWNS = {
    "basic_map": basic_map_enemies,
    "fountain_map": fountain_map_enemies,
}