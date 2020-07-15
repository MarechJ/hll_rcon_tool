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
    "stmariedumont_warfare": "St.Marie",
    "hurtgenforest_warfare": "Hurtgen", 
    "utahbeach_warfare": "Utah", 
    "omahabeach_offensive_us": "Omaha", 
    "stmereeglise_warfare": "SME",
    "stmereeglise_offensive_ger": "Off. SME(Ger)", 
    "foy_offensive_ger": "Off. Foy", 
    "purpleheartlane_warfare": "PHL",
    "purpleheartlane_offensive_us": "Off. PHL",
    "hill400_warfare": "Hill400",
    "hill400_offensive_US": "Off. Hill400",
    "stmereeglise_offensive_us": "Off. SME (US)",
    "carentan_warfare": "Carentan",
    "carentan_offensive_us": "Off. Carentan"
}