from enum import Enum

from rcon.maps import Team


class WeaponType(Enum):
    Infantry = "infantry"
    Bazooka = "bazooka"
    Grenade = "grenade"
    MachineGun = "machine_gun"
    Sniper = "sniper"
    Mine = "mine"
    PAK = "pak"
    Satchel = "satchel"
    Artillery = "artillery"
    Armor = "armor"
    Commander = "commander"


SOVIET_WEAPONS = {
    'PPSH 41': WeaponType.Infantry,
    'PPSH 41 W/DRUM': WeaponType.Infantry,
    'SVT40': WeaponType.Infantry,
    'MOSIN NAGANT 1891': WeaponType.Infantry,
    'MOSIN NAGANT 91/30': WeaponType.Infantry,
    'MOSIN NAGANT M38': WeaponType.Infantry,
    'DP-27': WeaponType.MachineGun,
    'SCOPED MOSIN NAGANT 91/30': WeaponType.Sniper,
    'SCOPED SVT40': WeaponType.Sniper,
    'NAGANT M1895': WeaponType.Infantry,
    'TOKAREV TT33': WeaponType.Infantry,
    'MPL-50 SPADE': WeaponType.Infantry,
    'RG-42 GRENADE': WeaponType.Grenade,
    'MOLOTOV': WeaponType.Grenade,
    'SATCHEL CHARGE': WeaponType.Satchel,
    'POMZ AP MINE': WeaponType.Mine,
    'TM-35 AT MINE': WeaponType.Mine,
    'PTRS-41': WeaponType.Infantry,
    'BAZOOKA': WeaponType.Bazooka,
    'FLARE GUN': WeaponType.Infantry,
    '122MM HOWITZER [M1938 (M-30)]': WeaponType.Artillery,
    '57MM CANNON [ZiS-2]': WeaponType.PAK,
    'BA-10': WeaponType.Armor,
    'T70': WeaponType.Armor,
    'T34/76': WeaponType.Armor,
    'IS-1': WeaponType.Armor,
    'M3 Half-track': WeaponType.Armor,
    'ZIS-5 (Transport)': WeaponType.Armor,
    'ZIS-5 (Supply)': WeaponType.Armor,
    'GAZ-67': WeaponType.Armor,
    '19-K 45MM [BA-10]': WeaponType.Armor,
    'COAXIAL DT [BA-10]': WeaponType.Armor,
    '45MM M1937 [T70]': WeaponType.Armor,
    'COAXIAL DT [T70]': WeaponType.Armor,
    '76MM ZiS-5 [T34/76]': WeaponType.Armor,
    'COAXIAL DT [T34/76]': WeaponType.Armor,
    'HULL DT [T34/76]': WeaponType.Armor,
    'D-5T 85MM [IS-1]': WeaponType.Armor,
    'COAXIAL DT [IS-1]': WeaponType.Armor,
    'HULL DT [IS-1]': WeaponType.Armor,
    'M2 Browning [M3 Half-track]': WeaponType.Armor,
}

BRITISH_WEAPONS = {
    # renamed to Sten Gun Mk.II
    'Sten Gun': WeaponType.Infantry,
    'Sten Gun Mk.II': WeaponType.Infantry,
    'Sten Gun Mk.V': WeaponType.Infantry,
    'Lanchester': WeaponType.Infantry,
    'M1928A1 THOMPSON': WeaponType.Infantry,
    'SMLE No.1 Mk III': WeaponType.Infantry,
    'Lee-Enfield Pattern 1914': WeaponType.Infantry,
    # deprecated (not in the game anymore)
    'Lee–Enfield Jungle Carbine': WeaponType.Infantry,
    # renamed to Rifle No.4 Mk I
    'Lee–Enfield No.4 Mk I': WeaponType.Infantry,
    'Rifle No.4 Mk I': WeaponType.Infantry,
    'Rifle No.5 Mk I': WeaponType.Infantry,
    'Bren Gun': WeaponType.MachineGun,
    'Lewis Gun': WeaponType.MachineGun,
    'Rifle No.4 Mk I Sniper': WeaponType.Sniper,
    'Lee-Enfield Pattern 1914 Sniper': WeaponType.Sniper,
    'Webley MK VI': WeaponType.Infantry,
    'FLAMETHROWER': WeaponType.Infantry,
    'Fairbairn–Sykes': WeaponType.Infantry,
    'Mills Bomb': WeaponType.Grenade,
    'No.82 Grenade': WeaponType.Grenade,
    'Satchel': WeaponType.Satchel,
    'A.P. Shrapnel Mine Mk II': WeaponType.Mine,
    'A.T. Mine G.S. Mk V': WeaponType.Mine,
    'PIAT': WeaponType.Infantry,
    'Boys Anti-tank Rifle': WeaponType.Infantry,
    'No.2 Mk 5 Flare Pistol': WeaponType.Infantry,
    'QF 25-POUNDER [QF 25-Pounder]': WeaponType.Artillery,
    'QF 6-POUNDER [QF 6-Pounder]': WeaponType.PAK,
    'Daimler': WeaponType.Armor,
    'Tetrarch': WeaponType.Armor,
    'Cromwell': WeaponType.Armor,
    'Firefly': WeaponType.Armor,
    'M3 Stuart Honey': WeaponType.Armor,
    'Churchill Mk.III': WeaponType.Armor,
    'M3 Half-track': WeaponType.Armor,
    'Bedford OYD (Transport)': WeaponType.Armor,
    'Bedford OYD (Supply)': WeaponType.Armor,
    'Jeep Willys': WeaponType.Armor,
    'QF 2-POUNDER [Daimler]': WeaponType.Armor,
    'COAXIAL BESA [Daimler]': WeaponType.Armor,
    'QF 2-POUNDER [Tetrarch]': WeaponType.Armor,
    'COAXIAL BESA [Tetrarch]': WeaponType.Armor,
    'COAXIAL BESA [Crusader Mk.III]': WeaponType.Armor,
    'OQF 57MM [Crusader Mk.III]': WeaponType.Armor,
    'OQF 57MM [Churchill Mk.III]': WeaponType.Armor,
    'QF 75MM [Cromwell]': WeaponType.Armor,
    'OQF 75MM [Cromwell]': WeaponType.Armor,
    'COAXIAL BESA [Cromwell]': WeaponType.Armor,
    '37MM CANNON [M3 Stuart Honey]': WeaponType.Armor,
    'COAXIAL M1919 [M3 Stuart Honey]': WeaponType.Armor,
    'OQF 6 - POUNDER Mk.V [Churchill Mk.III]': WeaponType.Armor,
    'COAXIAL BESA 7.92mm [Churchill Mk.III]': WeaponType.Armor,
    'COAXIAL BESA 7.92mm': WeaponType.Armor,
    'HULL BESA 7.92mm [Churchill Mk.III]': WeaponType.Armor,
    'HULL BESA [Cromwell]': WeaponType.Armor,
    'QF 17-POUNDER [Firefly]': WeaponType.Armor,
    'COAXIAL M1919 [Firefly]': WeaponType.Armor,
    'OQF 75MM [Churchill Mk.VII]': WeaponType.Armor,
    'COAXIAL BESA 7.92mm [Churchill Mk.VII]': WeaponType.Armor,
}

US_WEAPONS = {
    'M1A1 THOMPSON': WeaponType.Infantry,
    'M3 GREASE GUN': WeaponType.Infantry,
    'M1 GARAND': WeaponType.Infantry,
    'M1 CARBINE': WeaponType.Infantry,
    'M1918A2 BAR': WeaponType.Infantry,
    'M97 TRENCH GUN': WeaponType.Infantry,
    'BROWNING M1919': WeaponType.MachineGun,
    'M1919 SPRINGFIELD': WeaponType.Infantry,
    'M1903 SPRINGFIELD': WeaponType.Sniper,
    'COLT M1911': WeaponType.Infantry,
    'M2 FLAMETHROWER': WeaponType.Infantry,
    'M3 KNIFE': WeaponType.Infantry,
    'MK2 GRENADE': WeaponType.Grenade,
    'SATCHEL': WeaponType.Satchel,
    'M2 AP MINE': WeaponType.Mine,
    'M1A1 AT MINE': WeaponType.Mine,
    'BAZOOKA': WeaponType.Bazooka,
    'FLARE GUN': WeaponType.Infantry,
    '155MM HOWITZER [M114]': WeaponType.Artillery,
    '57MM CANNON [M1 57mm]': WeaponType.Armor,
    'M8 Greyhound': WeaponType.Armor,
    'Stuart M5A1': WeaponType.Armor,
    'Sherman M4A3(75)W': WeaponType.Armor,
    'Sherman M4A3E2': WeaponType.Armor,
    'Sherman M4A3E2(76)': WeaponType.Armor,
    'M3 Half-track': WeaponType.Armor,
    'GMC CCKW 363 (Transport)': WeaponType.Armor,
    'GMC CCKW 363 (Supply)': WeaponType.Armor,
    'GMC CCKW 353 (Supply)': WeaponType.Armor,
    'Jeep Willys': WeaponType.Armor,
    'M6 37mm [M8 Greyhound]': WeaponType.Armor,
    'COAXIAL M1919 [M8 Greyhound]': WeaponType.Armor,
    '37MM CANNON [Stuart M5A1]': WeaponType.Armor,
    'COAXIAL M1919 [Stuart M5A1]': WeaponType.Armor,
    'HULL M1919 [Stuart M5A1]': WeaponType.Armor,
    '75MM CANNON [Sherman M4A3(75)W]': WeaponType.Armor,
    'COAXIAL M1919 [Sherman M4A3(75)W]': WeaponType.Armor,
    'HULL M1919 [Sherman M4A3(75)W]': WeaponType.Armor,
    '75MM M3 GUN [Sherman M4A3E2]': WeaponType.Armor,
    'COAXIAL M1919 [Sherman M4A3E2]': WeaponType.Armor,
    'HULL M1919 [Sherman M4A3E2]': WeaponType.Armor,
    '76MM M1 GUN [Sherman M4A3E2(76)]': WeaponType.Armor,
    'COAXIAL M1919 [Sherman M4A3E2(76)]': WeaponType.Armor,
    'HULL M1919 [Sherman M4A3E2(76)]': WeaponType.Armor,
    'M2 Browning [M3 Half-track]': WeaponType.Armor,
}

AXIS_WEAPONS = {
    'MP40': WeaponType.Infantry,
    'GEWEHR 43': WeaponType.Infantry,
    'KARABINER 98K': WeaponType.Infantry,
    'STG44': WeaponType.Infantry,
    'FG42': WeaponType.Infantry,
    'MG34': WeaponType.MachineGun,
    'MG42': WeaponType.MachineGun,
    'KARABINER 98K x8': WeaponType.Sniper,
    'FG42 x4': WeaponType.Sniper,
    'WALTHER P38': WeaponType.Infantry,
    'LUGER P08': WeaponType.Infantry,
    'FLAMMENWERFER 41': WeaponType.Infantry,
    'FELDSPATEN': WeaponType.Infantry,
    'M24 STIELHANDGRANATE': WeaponType.Grenade,
    'M43 STIELHANDGRANATE': WeaponType.Grenade,
    'SATCHEL': WeaponType.Satchel,
    'S-MINE': WeaponType.Mine,
    'TELLERMINE 43': WeaponType.Mine,
    'PANZERSCHRECK': WeaponType.Bazooka,
    'FLARE GUN': WeaponType.Infantry,
    '150MM HOWITZER [sFH 18]': WeaponType.Artillery,
    '75MM CANNON [PAK 40]': WeaponType.PAK,
    'Sd.Kfz.234 Puma': WeaponType.Armor,
    'Sd.Kfz.121 Luchs': WeaponType.Armor,
    'Sd.Kfz.161 Panzer IV': WeaponType.Armor,
    'Sd.Kfz.181 Tiger 1': WeaponType.Armor,
    'Sd.Kfz.171 Panther': WeaponType.Armor,
    'Sd.Kfz 251 Half-track': WeaponType.Armor,
    'Opel Blitz (Transport)': WeaponType.Armor,
    'Opel Blitz (Supply)': WeaponType.Armor,
    'Kubelwagen': WeaponType.Armor,
    '50mm KwK 39/1 [Sd.Kfz.234 Puma]': WeaponType.Armor,
    'COAXIAL MG34': WeaponType.Armor,
    'COAXIAL MG34 [Sd.Kfz.234 Puma]': WeaponType.Armor,
    '20MM KWK 30 [Sd.Kfz.121 Luchs]': WeaponType.Armor,
    'COAXIAL MG34 [Sd.Kfz.121 Luchs]': WeaponType.Armor,
    '75MM CANNON [Sd.Kfz.161 Panzer IV]': WeaponType.Armor,
    'COAXIAL MG34 [Sd.Kfz.161 Panzer IV]': WeaponType.Armor,
    'HULL MG34 [Sd.Kfz.161 Panzer IV]': WeaponType.Armor,
    '75MM CANNON [Sd.Kfz.171 Panther]': WeaponType.Armor,
    'COAXIAL MG34 [Sd.Kfz.171 Panther]': WeaponType.Armor,
    'HULL MG34 [Sd.Kfz.171 Panther]': WeaponType.Armor,
    '88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]': WeaponType.Armor,
    'COAXIAL MG34 [Sd.Kfz.181 Tiger 1]': WeaponType.Armor,
    'HULL MG34 [Sd.Kfz.181 Tiger 1]': WeaponType.Armor,
    'MG 42 [Sd.Kfz 251 Half-track]': WeaponType.Armor,
}

ALL_WEAPONS = {
    **US_WEAPONS,
    **SOVIET_WEAPONS,
    **BRITISH_WEAPONS,
    **AXIS_WEAPONS,
    'BOMBING RUN': WeaponType.Commander,
    'STRAFING RUN': WeaponType.Commander,
    'PRECISION STRIKE': WeaponType.Commander,
}

NO_SIDE_WEAPONS = [
    'UNKNOWN',
    'BOMBING RUN',
    'STRAFING RUN',
    'PRECISION STRIKE',
    'BAZOOKA',
    'SATCHEL',
    'FLARE GUN',
    'M3 Half-track',
    'M2 Browning [M3 Half-track]',
    'Jeep Willys',
]

WEAPON_SIDE_MAP = {}

for w in [*US_WEAPONS.keys(), *SOVIET_WEAPONS.keys(), *BRITISH_WEAPONS.keys()]:
    if w in NO_SIDE_WEAPONS:
        continue
    WEAPON_SIDE_MAP[w] = Team.ALLIES

for w in AXIS_WEAPONS.keys():
    if w in NO_SIDE_WEAPONS:
        continue
    WEAPON_SIDE_MAP[w] = Team.AXIS
