#This file will contain all enemy spawn locations for each level as well as
#Doordinates , Type of Enemy , Health , etc.

basic_map_enemies = [
    {"x": 15, "y": 11, "type": "ghost", "pattern": "vertical", "health": 50},
    {"x": 10 , "y": 10 , "type": "ninja" , "pattern": "horizontal" , "health": 70}
]

fountain_map_enemies = [
        {"x": 18, "y": 9, "type": "ghost", "pattern": "vertical", "health": 150},
        {"x": 5 , "y": 8 , "type": "ninja" , "pattern": "horizontal" , "health": 100}
]

ENEMY_SPAWNS = {
    "basic_map": basic_map_enemies,
    "fountain_map": fountain_map_enemies,
}