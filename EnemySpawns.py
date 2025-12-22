#This file will contain all enemy spawn locations for each level as well as
#Doordinates , Type of Enemy , Health , etc.

basic_map_enemies = [
    {"x": 15, "y": 11, "type": "ghost", "pattern": "vertical", "health": 50},
    {"x": 18, "y": 8, "type": "ghost", "pattern": "horizontal", "health": 40},
    {"x": 10, "y": 5, "type": "ghost", "pattern": "chase", "health": 60},
]

ENEMY_SPAWNS = {
    "basic_map_enemies": basic_map_enemies,
}