import random


maps = ["foy_warfare", "stmariedumont_warfare", "hurtgenforest_warfare", 
"utahbeach_warfare", "omahabeach_offensive_us", "stmereeglise_warfare", 
"stmereeglise_offensive_ger", "foy_offensive_ger", "purpleheartlane_warfare", 
"purpleheartlane_offensive_us"]


rand = random.choice(maps)
held = []
actual_help = []
rotation = []
actual = []

for m in rand:
    name, mode = m.split("_", 1)
    if mode.startswith('offensive'):
        mod, side = mode.split('_')
    if name == rotation[-1] and mode:
        print("skipping duplicate")
        held.append(name)
        actual_help.append(name + mode)
        continue
    rotation.append(name)
    actual.append(name + mode)