import { Faceoff, Player, ServerFinalStats } from '@/types/player'
import { Weapon, WeaponCategory } from '@/types/weapon'

// LIST OF WEAPONS
// https://gist.github.com/timraay/5634d85eab552b5dfafb9fd61273dc52#available-weapons
export const axisWeapons: Set<Weapon> = new Set([
  'MP40',
  'GEWEHR 43',
  'KARABINER 98K',
  'STG44',
  'FG42',
  'MG34',
  'MG42',
  'KARABINER 98K x8',
  'FG42 x4',
  'WALTHER P38',
  'LUGER P08',
  'FLAMMENWERFER 41',
  'FELDSPATEN',
  // "M24 STIELHANDGRANATE",
  // "M43 STIELHANDGRANATE",
  // "TELLERMINE 43",
  'PANZERSCHRECK',
  '150MM HOWITZER [sFH 18]',
  '75MM CANNON [PAK 40]',
  // "Sd.Kfz.234 Puma",
  // "Sd.Kfz.121 Luchs",
  // "Sd.Kfz.161 Panzer IV",
  // "Sd.Kfz.181 Tiger 1",
  // "Sd.Kfz.171 Panther",
  // "Sd.Kfz 251 Half-track",
  // "Opel Blitz (Transport)",
  // "Opel Blitz (Supply)",
  // "Kubelwagen",
  '50mm KwK 39/1 [Sd.Kfz.234 Puma]',
  'COAXIAL MG34 [Sd.Kfz.234 Puma]',
  '20MM KWK 30 [Sd.Kfz.121 Luchs]',
  'COAXIAL MG34 [Sd.Kfz.121 Luchs]',
  '75MM CANNON [Sd.Kfz.161 Panzer IV]',
  'COAXIAL MG34 [Sd.Kfz.161 Panzer IV]',
  'HULL MG34 [Sd.Kfz.161 Panzer IV]',
  '75MM CANNON [Sd.Kfz.171 Panther]',
  'COAXIAL MG34 [Sd.Kfz.171 Panther]',
  'HULL MG34 [Sd.Kfz.171 Panther]',
  '88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]',
  'COAXIAL MG34 [Sd.Kfz.181 Tiger 1]',
  'HULL MG34 [Sd.Kfz.181 Tiger 1]',
  'MG 42 [Sd.Kfz 251 Half-track]',
])

export const tankWeapons = new Set([
  // M8 Greyhound
  'M6 37mm [M8 Greyhound]',
  'COAXIAL M1919 [M8 Greyhound]',
  // Stuart M5A1
  '37MM CANNON [Stuart M5A1]',
  'COAXIAL M1919 [Stuart M5A1]',
  'HULL M1919 [Stuart M5A1]',
  // Sherman M4A3(75)W
  '75MM CANNON [Sherman M4A3(75)W]',
  'COAXIAL M1919 [Sherman M4A3(75)W]',
  'HULL M1919 [Sherman M4A3(75)W]',
  // Sherman M4A3E2 "75mm"
  '75MM M3 GUN [Sherman M4A3E2]',
  'COAXIAL M1919 [Sherman M4A3E2]',
  'HULL M1919 [Sherman M4A3E2]',
  // Sherman M4A3E2 "76mm"
  '76MM M1 GUN [Sherman M4A3E2(76)]',
  'COAXIAL M1919 [Sherman M4A3E2(76)]',
  'HULL M1919 [Sherman M4A3E2(76)]',
  // Sd.Kfz.234 Puma
  '50mm KwK 39/1 [Sd.Kfz.234 Puma]',
  'COAXIAL MG34 [Sd.Kfz.234 Puma]',
  // Sd.Kfz.121 Luchs
  '20MM KWK 30 [Sd.Kfz.121 Luchs]',
  'COAXIAL MG34 [Sd.Kfz.121 Luchs]',
  // Sd.Kfz.161 Panzer IV
  '75MM CANNON [Sd.Kfz.161 Panzer IV]',
  'COAXIAL MG34 [Sd.Kfz.161 Panzer IV]',
  'HULL MG34 [Sd.Kfz.161 Panzer IV]',
  // Sd.Kfz.171 Panther
  '75MM CANNON [Sd.Kfz.171 Panther]',
  'COAXIAL MG34 [Sd.Kfz.171 Panther]',
  'HULL MG34 [Sd.Kfz.171 Panther]',
  // Sd.Kfz.181 Tiger 1
  '88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]',
  'COAXIAL MG34 [Sd.Kfz.181 Tiger 1]',
  'HULL MG34 [Sd.Kfz.181 Tiger 1]',
  // BA-10
  '19-K 45MM [BA-10]',
  'COAXIAL DT [BA-10]',
  // T70
  '45MM M1937 [T70]',
  'COAXIAL DT [T70]',
  // T34/76
  '76MM ZiS-5 [T34/76]',
  'COAXIAL DT [T34/76]',
  'HULL DT [T34/76]',
  // IS-1
  'D-5T 85MM [IS-1]',
  'COAXIAL DT [IS-1]',
  'HULL DT [IS-1]',
  // Tetrarch
  'QF 2-POUNDER [Tetrarch]',
  'COAXIAL BESA [Tetrarch]',
  // Cromwell
  'QF 75MM [Cromwell]',
  'COAXIAL BESA [Cromwell]',
  'HULL BESA [Cromwell]',
  // Firefly
  'QF 17-POUNDER [Firefly]',
  'COAXIAL M1919 [Firefly]',
])

export const isArtillery = (weapons: Player['weapons']) => {
  const artilleryWeapons = [
    '150MM HOWITZER [sFH 18]',
    '155MM HOWITZER [M114]',
    '122MM HOWITZER [M1938 (M-30)]',
    'QF 25-POUNDER [QF 25-Pounder]',
  ]
  return artilleryWeapons.some((weapon) => weapon in weapons)
}

export const isCommander = (weapons: Player['weapons']) => {
  const commanderWeapons = ['BOMBING RUN', 'STRAFING RUN', 'PRECISION STRIKE']
  return commanderWeapons.some((weapon) => weapon in weapons)
}

export const isTankCrew = (player: Player) => {
  return Object.keys(player.weapons).find((weapon) => tankWeapons.has(weapon))
}

export const weaponCategories: WeaponCategory[] = [
  'Submachine Gun',
  'Semi-Auto Rifle',
  'Bolt-Action Rifle',
  'Assault Rifle',
  'Machine Gun',
  'Sniper Rifle',
  'Anti-Tank Rifle',
  'Artillery Gun',
  'Anti-Tank Gun',
  'Recon Vehicle',
  'Light Tank',
  'Medium Tank',
  'Heavy Tank',
  'Commander ability',
  'Pistol',
  'Grenade',
  'Satchel Charge',
  'Anti-Personnel Mine',
  'Anti-Tank Mine',
  'Shotgun',
  'Half-track',
  'Roadkill',
  'Melee Weapon',
  'Flamethrower',
  'Flare Gun',
  'UNKNOWN',
]

export const weaponCategoryMap: Record<Weapon, WeaponCategory> = {
  UNKNOWN: 'UNKNOWN',
  Unknown: 'UNKNOWN',

  // United States (US) Weapons
  'M1A1 THOMPSON': 'Submachine Gun',
  'M3 GREASE GUN': 'Submachine Gun',
  'M1 GARAND': 'Semi-Auto Rifle',
  'M1 CARBINE': 'Semi-Auto Rifle',
  'M1917 ENFIELD': 'Bolt-Action Rifle',
  'M1918A2 BAR': 'Assault Rifle',
  'M97 TRENCH GUN': 'Shotgun',
  'BROWNING M1919': 'Machine Gun',
  'M1919 SPRINGFIELD': 'Sniper Rifle',
  'M1903 SPRINGFIELD': 'Sniper Rifle',
  'COLT M1911': 'Pistol',
  'M2 FLAMETHROWER': 'Flamethrower',
  'M3 KNIFE': 'Melee Weapon',
  'MK2 GRENADE': 'Grenade',
  SATCHEL: 'Satchel Charge',
  'M2 AP MINE': 'Anti-Personnel Mine',
  'M1A1 AT MINE': 'Anti-Tank Mine',
  BAZOOKA: 'Anti-Tank Rifle',
  'FLARE GUN': 'Flare Gun',

  // Germany (GER) Weapons
  MP40: 'Submachine Gun',
  'GEWEHR 43': 'Semi-Auto Rifle',
  'KARABINER 98K': 'Bolt-Action Rifle',
  STG44: 'Assault Rifle',
  FG42: 'Assault Rifle',
  MG34: 'Machine Gun',
  MG42: 'Machine Gun',
  'KARABINER 98K x8': 'Sniper Rifle',
  'FG42 x4': 'Sniper Rifle',
  'WALTHER P38': 'Pistol',
  'LUGER P08': 'Pistol',
  'FLAMMENWERFER 41': 'Flamethrower',
  FELDSPATEN: 'Melee Weapon',
  'M24 STIELHANDGRANATE': 'Grenade',
  'M43 STIELHANDGRANATE': 'Grenade',
  'S-MINE': 'Anti-Personnel Mine',
  'TELLERMINE 43': 'Anti-Tank Mine',
  PANZERSCHRECK: 'Anti-Tank Rifle',

  // Soviet Union (RUS) Weapons
  'PPSH 41': 'Submachine Gun',
  'PPSH 41 W/DRUM': 'Submachine Gun',
  SVT40: 'Semi-Auto Rifle',
  'MOSIN NAGANT 1891': 'Bolt-Action Rifle',
  'MOSIN NAGANT 91/30': 'Bolt-Action Rifle',
  'MOSIN NAGANT M38': 'Bolt-Action Rifle',
  'DP-27': 'Machine Gun',
  'SCOPED MOSIN NAGANT 91/30': 'Sniper Rifle',
  'SCOPED SVT40': 'Sniper Rifle',
  'NAGANT M1895': 'Pistol',
  'TOKAREV TT33': 'Pistol',
  FLAMETHROWER: 'Flamethrower',
  'MPL-50 SPADE': 'Melee Weapon',
  'RG-42 GRENADE': 'Grenade',
  MOLOTOV: 'Grenade',
  'SATCHEL CHARGE': 'Satchel Charge',
  'POMZ AP MINE': 'Anti-Personnel Mine',
  'TM-35 AT MINE': 'Anti-Tank Mine',
  'PTRS-41': 'Anti-Tank Rifle',
  PIAT: 'Anti-Tank Rifle',

  // Great Britain (GB) Weapons
  'Sten Gun Mk.II': 'Submachine Gun',
  'Sten Gun Mk.V': 'Submachine Gun',
  Lanchester: 'Submachine Gun',
  'M1928A1 THOMPSON': 'Submachine Gun',
  'SMLE No.1 Mk III': 'Bolt-Action Rifle',
  'Lee-Enfield Pattern 1914': 'Bolt-Action Rifle',
  'Rifle No.4 Mk I': 'Bolt-Action Rifle',
  'Rifle No.5 Mk I': 'Bolt-Action Rifle',
  'Lewis Gun': 'Machine Gun',
  'Bren Gun': 'Assault Rifle',
  'Lee-Enfield Pattern 1914 Sniper': 'Sniper Rifle',
  'Rifle No.4 Mk I Sniper': 'Sniper Rifle',
  'Webley MK VI': 'Pistol',
  'Mills Bomb': 'Grenade',
  'No.82 Grenade': 'Grenade',
  Satchel: 'Satchel Charge',
  'A.T. Mine G.S. Mk V': 'Anti-Tank Mine',
  'No.2 Mk 5 Flare Pistol': 'Flare Gun',
  'A.P. Shrapnel Mine Mk II': 'Anti-Personnel Mine',
  'Fairbairn–Sykes': 'Melee Weapon',

  // United States (US) Weapons
  '155MM HOWITZER [M114]': 'Artillery Gun',
  '57MM CANNON [M1 57mm]': 'Anti-Tank Gun',

  // Germany (GER) Weapons
  '150MM HOWITZER [sFH 18]': 'Artillery Gun',
  '75MM CANNON [PAK 40]': 'Anti-Tank Gun',

  // Soviet Union (RUS) Weapons
  '122MM HOWITZER [M1938 (M-30)]': 'Artillery Gun',
  '57MM CANNON [ZiS-2]': 'Anti-Tank Gun',

  // Great Britain (GB) Weapons
  'QF 25-POUNDER [QF 25-Pounder]': 'Artillery Gun',
  'QF 6-POUNDER [QF 6-Pounder]': 'Anti-Tank Gun',

  // Vehicles (Roadkills)
  // United States (US) Vehicles
  'M8 Greyhound': 'Roadkill',
  'Stuart M5A1': 'Roadkill',
  'Sherman M4A3(75)W': 'Roadkill',
  'Sherman M4A3E2': 'Roadkill',
  'Sherman M4A3E2(76)': 'Roadkill',
  'M3 Half-track': 'Roadkill',
  'GMC CCKW 353 (Transport)': 'Roadkill',
  'GMC CCKW 353 (Supply)': 'Roadkill',
  'Jeep Willys': 'Roadkill',

  // Germany (GER) Vehicles
  'Sd.Kfz.234 Puma': 'Roadkill',
  'Sd.Kfz.121 Luchs': 'Roadkill',
  'Sd.Kfz.161 Panzer IV': 'Roadkill',
  'Sd.Kfz.181 Tiger 1': 'Roadkill',
  'Sd.Kfz.171 Panther': 'Roadkill',
  'Sd.Kfz 251 Half-track': 'Roadkill',
  'Opel Blitz (Transport)': 'Roadkill',
  'Opel Blitz (Supply)': 'Roadkill',
  Kubelwagen: 'Roadkill',

  // Soviet Union (RUS) Vehicles
  'BA-10': 'Roadkill',
  T70: 'Roadkill',
  'T34/76': 'Roadkill',
  'IS-1': 'Roadkill',
  'ZIS-5 (Transport)': 'Roadkill',
  'ZIS-5 (Supply)': 'Roadkill',
  'GAZ-67': 'Roadkill',

  // Great Britain (GB) Vehicles
  Daimler: 'Roadkill',
  Tetrarch: 'Roadkill',
  'M3 Stuart Honey': 'Roadkill',
  Cromwell: 'Roadkill',
  'Crusader Mk.III': 'Roadkill',
  Firefly: 'Roadkill',
  'Churchill Mk.III': 'Roadkill',
  'Churchill Mk.VII': 'Roadkill',
  'Bedford OYD (Transport)': 'Roadkill',
  'Bedford OYD (Supply)': 'Roadkill',

  // United States (US) Vehicles
  'M6 37mm [M8 Greyhound]': 'Recon Vehicle',
  'COAXIAL M1919 [M8 Greyhound]': 'Recon Vehicle',
  '37MM CANNON [Stuart M5A1]': 'Light Tank',
  'COAXIAL M1919 [Stuart M5A1]': 'Light Tank',
  'HULL M1919 [Stuart M5A1]': 'Light Tank',
  '75MM CANNON [Sherman M4A3(75)W]': 'Medium Tank',
  'COAXIAL M1919 [Sherman M4A3(75)W]': 'Medium Tank',
  'HULL M1919 [Sherman M4A3(75)W]': 'Medium Tank',
  '75MM M3 GUN [Sherman M4A3E2]': 'Heavy Tank',
  'COAXIAL M1919 [Sherman M4A3E2]': 'Heavy Tank',
  'HULL M1919 [Sherman M4A3E2]': 'Heavy Tank',
  '76MM M1 GUN [Sherman M4A3E2(76)]': 'Heavy Tank',
  'COAXIAL M1919 [Sherman M4A3E2(76)]': 'Heavy Tank',
  'HULL M1919 [Sherman M4A3E2(76)]': 'Heavy Tank',
  'M2 Browning [M3 Half-track]': 'Half-track',

  // Germany (GER) Vehicles
  '50mm KwK 39/1 [Sd.Kfz.234 Puma]': 'Recon Vehicle',
  'COAXIAL MG34 [Sd.Kfz.234 Puma]': 'Recon Vehicle',
  '20MM KWK 30 [Sd.Kfz.121 Luchs]': 'Light Tank',
  'COAXIAL MG34 [Sd.Kfz.121 Luchs]': 'Light Tank',
  '75MM CANNON [Sd.Kfz.161 Panzer IV]': 'Medium Tank',
  'COAXIAL MG34 [Sd.Kfz.161 Panzer IV]': 'Medium Tank',
  'HULL MG34 [Sd.Kfz.161 Panzer IV]': 'Medium Tank',
  '75MM CANNON [Sd.Kfz.171 Panther]': 'Heavy Tank',
  'COAXIAL MG34 [Sd.Kfz.171 Panther]': 'Heavy Tank',
  'HULL MG34 [Sd.Kfz.171 Panther]': 'Heavy Tank',
  '88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]': 'Heavy Tank',
  'COAXIAL MG34 [Sd.Kfz.181 Tiger 1]': 'Heavy Tank',
  'HULL MG34 [Sd.Kfz.181 Tiger 1]': 'Heavy Tank',
  'MG 42 [Sd.Kfz 251 Half-track]': 'Half-track',

  // Soviet Union (RUS) Vehicles
  '19-K 45MM [BA-10]': 'Recon Vehicle',
  'COAXIAL DT [BA-10]': 'Recon Vehicle',
  '45MM M1937 [T70]': 'Light Tank',
  'COAXIAL DT [T70]': 'Light Tank',
  '76MM ZiS-5 [T34/76]': 'Medium Tank',
  'COAXIAL DT [T34/76]': 'Medium Tank',
  'HULL DT [T34/76]': 'Medium Tank',
  'D-5T 85MM [IS-1]': 'Heavy Tank',
  'COAXIAL DT [IS-1]': 'Heavy Tank',
  'HULL DT [IS-1]': 'Heavy Tank',

  // Great Britain (GB) Vehicles
  'QF 2-POUNDER [Daimler]': 'Recon Vehicle',
  'COAXIAL BESA [Daimler]': 'Recon Vehicle',
  'QF 2-POUNDER [Tetrarch]': 'Light Tank',
  'COAXIAL BESA [Tetrarch]': 'Light Tank',
  '37MM CANNON [M3 Stuart Honey]': 'Light Tank',
  'COAXIAL M1919 [M3 Stuart Honey]': 'Light Tank',
  'HULL M1919 [M3 Stuart Honey]': 'Light Tank',
  'OQF 75MM [Cromwell]': 'Medium Tank',
  'COAXIAL BESA [Cromwell]': 'Medium Tank',
  'HULL BESA [Cromwell]': 'Medium Tank',
  'OQF 57MM [Crusader Mk.III]': 'Medium Tank',
  'COAXIAL BESA [Crusader Mk.III]': 'Medium Tank',
  'QF 17-POUNDER [Firefly]': 'Heavy Tank',
  'COAXIAL M1919 [Firefly]': 'Heavy Tank',
  'OQF 57MM [Churchill Mk.III]': 'Heavy Tank',
  'COAXIAL BESA 7.92mm [Churchill Mk.III]': 'Heavy Tank',
  'HULL BESA 7.92mm [Churchill Mk.III]': 'Heavy Tank',
  'OQF 57MM [Churchill Mk.VII]': 'Heavy Tank',
  'OQF 75MM [Churchill Mk.VII]': 'Heavy Tank',
  'COAXIAL BESA 7.92mm [Churchill Mk.VII]': 'Heavy Tank',
  'HULL BESA 7.92mm [Churchill Mk.VII]': 'Heavy Tank',

  // Commander
  'BOMBING RUN': 'Commander ability',
  'STRAFING RUN': 'Commander ability',
  'PRECISION STRIKE': 'Commander ability',
}

type KillCategory = 'infantry' | 'armor' | 'artillery' | 'other'

export const getKillCategory = (weapon: Weapon): KillCategory => {
  switch (weaponCategoryMap[weapon]) {
    case 'Light Tank':
    case 'Medium Tank':
    case 'Heavy Tank':
    case 'Recon Vehicle':
      return 'armor'
    case 'Artillery Gun':
      return 'artillery'
    case 'Commander ability':
    case 'Roadkill':
    case 'UNKNOWN':
      return 'other'
    default:
      return 'infantry'
  }
}

export const getLiveStats = (data: ServerFinalStats) => {
  // Sort players by kill count
  const players = data.result.player_stats as Player[]
  players.sort((a, b) => b.kills - a.kills)
  return players
}

export function mergeKillsDeaths(player: Player) {
  const { most_killed: killsByPlayer, death_by: deathsByPlayer } = player
  const allPlayerNames = new Set(Object.keys(killsByPlayer).concat(Object.keys(deathsByPlayer)))
  const merged: Faceoff[] = []
  allPlayerNames.forEach((name) => {
    merged.push({
      name: name,
      kills: killsByPlayer[name] ?? 0,
      deaths: deathsByPlayer[name] ?? 0,
      diff: (killsByPlayer[name] ?? 0) - (deathsByPlayer[name] ?? 0),
    })
  })
  merged.sort((a, b) => b.kills - a.kills)
  return merged
}
