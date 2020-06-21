def number_to_map(rcon):
    return {
        str(idx): map_
        for idx, map_ in enumerate(sorted(rcon.get_maps()))
    }


HUMAN_MAP_NAMES = {
    "foy_warfare": "Foy",
    "stmariedumont_warfare": "St. Marie du Mont",
    "hurtgenforest_warfare": "Hurtgen Forest", 
    "utahbeach_warfare": "Utah Beach", 
    "omahabeach_offensive_us": "Omaha Beach", 
    "stmereeglise_warfare": "St Mere Eglise",
    "stmereeglise_offensive_ger": "Off. St Mere Eglise (Ger)", 
    "foy_offensive_ger": "Off. Foy", 
    "purpleheartlane_warfare": "Purple Heart Lane",
    "purpleheartlane_offensive_us": "Off. Purple Heart Lane",
    "hill400_warfare": "Hill 400",
    "hill400_offensive_US": "Off. Hill 400",
    "stmereeglise_offensive_us": "Off. St Mere Eglise (US)"
}