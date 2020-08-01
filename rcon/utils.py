def number_to_map(rcon):
    return {
        str(idx): map_
        for idx, map_ in enumerate(sorted(rcon.get_maps()))
    }


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
    "stmereeglise_offensive_us": "Off. SME (US)"
}