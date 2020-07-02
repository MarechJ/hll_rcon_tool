def get_current_map(rcon):
    map_ = rcon.get_map()

    if map_.endswith('_RESTART'):
        map_ = map_.replace('_RESTART', '')

    return map_

def number_to_map(rcon):
    mapping = {}
    current = get_current_map(rcon)

    for idx, map_ in enumerate(sorted(rcon.get_maps())):
        if map_ == current:
            idx = 'x'
        mapping[str(idx)] = map_
    
    return mapping



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