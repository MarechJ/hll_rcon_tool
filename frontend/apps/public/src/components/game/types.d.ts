type Team = {
    name: string;
    side: "allies" | "axis";
    score: number;
    img: string;
    country: string;
  };
  
  type Teams = {
    home: Team;
    away: Team;
  };
  
  type League = {
    name: string;
    img: string;
  };
  
  type LinkBase = {
    url: string;
    title: string;
    author: string;
    date: string;
    description: string;
  };
  
  type TwitchLink = LinkBase & {
    type: "twitch";
  };
  
  type YoutubeLink = LinkBase & {
    type: "youtube";
  };
  
  type Link = TwitchLink | YoutubeLink;
  
  interface MatchBase {
    id: number;
    date: string;
    time: string;
    league: League;
    format: string;
    aside: string;
    teams: Teams;
    links?: Link[];
    map: string;
  }
  
  interface CompletedMatch extends MatchBase {
    length: number;
    completed: true;
    points?: string[];
  }
  
  interface ScheduledMatch extends MatchBase {
    completed: false;
  }
  
  export type Match = CompletedMatch | ScheduledMatch;
  
  export interface ServerFinalStats {
    result: Result;
    command: string;
    arguments?: null;
    failed: boolean;
    error?: null;
    forwards_results?: null;
  }
  
  export interface Result {
    id: number;
    creation_time: string;
    start: string;
    end: string;
    server_number: number;
    map_name: string;
    player_stats?: Player[] | null;
  }

  interface PlayerBase {
    player_id: number;
    steam_id_64: string;
    player: string;
    steaminfo?: Steaminfo;
    map_id: number;
    kills: number;
    kills_streak: number;
    deaths: number;
    deaths_without_kill_streak: number;
    teamkills: number;
    teamkills_streak: number;
    deaths_by_tk: number;
    deaths_by_tk_streak: number;
    nb_vote_started: number;
    nb_voted_yes: number;
    nb_voted_no: number;
    time_seconds: number;
    kills_per_minute: number;
    deaths_per_minute: number;
    kill_death_ratio: number;
    longest_life_secs: number;
    shortest_life_secs: number;
    combat: number;
    offense: number;
    defense: number;
    support: number;
    most_killed: Record<string, number>;
    death_by: Record<string, number>;
    weapons: Record<Weapon, number>;
    death_by_weapons: Record<Weapon, number>;
  }

  export interface Playerv10 {
    player_id: number;
    steam_id_64: string;
    player: string;
    steaminfo?: Steaminfo;
    map_id: number;
    kills: number;
    kills_streak: number;
    deaths: number;
    deaths_without_kill_streak: number;
    teamkills: number;
    teamkills_streak: number;
    deaths_by_tk: number;
    deaths_by_tk_streak: number;
    nb_vote_started: number;
    nb_voted_yes: number;
    nb_voted_no: number;
    time_seconds: number;
    kills_per_minute: number;
    deaths_per_minute: number;
    kill_death_ratio: number;
    longest_life_secs: number;
    shortest_life_secs: number;
    combat: number;
    offense: number;
    defense: number;
    support: number;
    most_killed: Record<string, number>;
    death_by: Record<string, number>;
    weapons: Record<Weapon, number>;
    death_by_weapons: Record<Weapon, number>;
  }
  
  export interface Player {
    id: number;
    player_id: string;
    steam_id_64: string;
    player: string;
    steaminfo?: Steaminfo;
    map_id: number;
    kills: number;
    kills_streak: number;
    deaths: number;
    deaths_without_kill_streak: number;
    teamkills: number;
    teamkills_streak: number;
    deaths_by_tk: number;
    deaths_by_tk_streak: number;
    nb_vote_started: number;
    nb_voted_yes: number;
    nb_voted_no: number;
    time_seconds: number;
    kills_per_minute: number;
    deaths_per_minute: number;
    kill_death_ratio: number;
    longest_life_secs: number;
    shortest_life_secs: number;
    combat: number;
    offense: number;
    defense: number;
    support: number;
    most_killed: Record<string, number>;
    death_by: Record<string, number>;
    weapons: Record<Weapon, number>;
    death_by_weapons: Record<Weapon, number>;
  }
  
  export interface Steaminfo {
    id: number;
    created: string;
    updated: string | null;
    profile: Profile | null;
    country: string | null;
    bans: any | null;
    has_bans: boolean;
  }
  
  export interface Profile {
    avatar: string;
    gameid: string;
    steamid: string;
    realname: string;
    loccityid: number;
    avatarfull: string;
    avatarhash: string;
    lastlogoff: number;
    profileurl: string;
    personaname: string;
    timecreated: number;
    avatarmedium: string;
    gameserverip: string;
    locstatecode: string;
    personastate: number;
    profilestate: number;
    gameextrainfo: string;
    primaryclanid: string;
    loccountrycode: string;
    gameserversteamid: string;
    personastateflags: number;
    communityvisibilitystate: number;
  }
  
  // United States (US) Weapons
  type US_Weapon =
    | "M1A1 THOMPSON"
    | "M3 GREASE GUN"
    | "M1 GARAND"
    | "M1 CARBINE"
    | "M1917 ENFIELD"
    | "M1918A2 BAR"
    | "M97 TRENCH GUN"
    | "BROWNING M1919"
    | "M1919 SPRINGFIELD"
    | "M1903 SPRINGFIELD"
    | "COLT M1911"
    | "M2 FLAMETHROWER"
    | "M3 KNIFE"
    | "MK2 GRENADE"
    | "SATCHEL"
    | "M2 AP MINE"
    | "M1A1 AT MINE"
    | "BAZOOKA"
    | "FLARE GUN"
    | "155MM HOWITZER [M114]"
    | "57MM CANNON [M1 57mm]"
  
  // Germany (GER) Weapons
  type GER_Weapon =
    | "MP40"
    | "GEWEHR 43"
    | "KARABINER 98K"
    | "STG44"
    | "FG42"
    | "MG34"
    | "MG42"
    | "KARABINER 98K x8"
    | "FG42 x4"
    | "WALTHER P38"
    | "LUGER P08"
    | "FLAMMENWERFER 41"
    | "FELDSPATEN"
    | "M24 STIELHANDGRANATE"
    | "M43 STIELHANDGRANATE"
    | "SATCHEL"
    | "S-MINE"
    | "TELLERMINE 43"
    | "PANZERSCHRECK"
    | "FLARE GUN"
    | "150MM HOWITZER [sFH 18]"
    | "75MM CANNON [PAK 40]"
  
  // Soviet Union (RUS) Weapons
  type RUS_Weapon =
    | "PPSH 41"
    | "PPSH 41 W/DRUM"
    | "SVT40"
    | "MOSIN NAGANT 1891"
    | "MOSIN NAGANT 91/30"
    | "MOSIN NAGANT M38"
    | "DP-27"
    | "SCOPED MOSIN NAGANT 91/30"
    | "SCOPED SVT40"
    | "NAGANT M1895"
    | "TOKAREV TT33"
    | "FLAMETHROWER"
    | "MPL-50 SPADE"
    | "RG-42 GRENADE"
    | "MOLOTOV"
    | "SATCHEL CHARGE"
    | "POMZ AP MINE"
    | "TM-35 AT MINE"
    | "PTRS-41"
    | "PIAT"
    | "FLARE GUN"
    | "122MM HOWITZER [M1938 (M-30)]"
    | "57MM CANNON [ZiS-2]"
  
  // Great Britain (GB) Weapons
  type GB_Weapon =
    | "Sten Gun Mk.II"
    | "Lewis Gun"
    | "Sten Gun Mk.V"
    | "Lanchester"
    | "M1928A1 THOMPSON"
    | "SMLE No.1 Mk III"
    | "Lee-Enfield Pattern 1914"
    | "Rifle No.4 Mk I"
    | "Rifle No.5 Mk I"
    | "Bren Gun"
    | "Lee-Enfield Pattern 1914 Sniper"
    | "Rifle No.4 Mk I Sniper"
    | "Webley MK VI"
    | "Mills Bomb"
    | "No.82 Grenade"
    | "Satchel"
    | "A.T. Mine G.S. Mk V"
    | "No.2 Mk 5 Flare Pistol"
    | "QF 25-POUNDER [QF 25-Pounder]"
    | "QF 6-POUNDER [QF 6-Pounder]"
    | "A.P. Shrapnel Mine Mk II"
    | "Fairbairn–Sykes"
  
  type InfantryWeapon = US_Weapon | GER_Weapon | RUS_Weapon | GB_Weapon
  
  type US_ArmorWeapon = "M6 37mm [M8 Greyhound]" | "COAXIAL M1919 [M8 Greyhound]" | "37MM CANNON [Stuart M5A1]" | "COAXIAL M1919 [Stuart M5A1]" | "HULL M1919 [Stuart M5A1]" | "75MM CANNON [Sherman M4A3(75)W]" | "COAXIAL M1919 [Sherman M4A3(75)W]" | "HULL M1919 [Sherman M4A3(75)W]" | "75MM M3 GUN [Sherman M4A3E2]" | "COAXIAL M1919 [Sherman M4A3E2]" | "HULL M1919 [Sherman M4A3E2]" | "76MM M1 GUN [Sherman M4A3E2(76)]" | "COAXIAL M1919 [Sherman M4A3E2(76)]" | "HULL M1919 [Sherman M4A3E2(76)]" | "M2 Browning [M3 Half-track]";
  
  type GER_ArmorWeapon = "50mm KwK 39/1 [Sd.Kfz.234 Puma]" | "COAXIAL MG34 [Sd.Kfz.234 Puma]" | "20MM KWK 30 [Sd.Kfz.121 Luchs]" | "COAXIAL MG34 [Sd.Kfz.121 Luchs]" | "75MM CANNON [Sd.Kfz.161 Panzer IV]" | "COAXIAL MG34 [Sd.Kfz.161 Panzer IV]" | "HULL MG34 [Sd.Kfz.161 Panzer IV]" | "75MM CANNON [Sd.Kfz.171 Panther]" | "COAXIAL MG34 [Sd.Kfz.171 Panther]" | "HULL MG34 [Sd.Kfz.171 Panther]" | "88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]" | "COAXIAL MG34 [Sd.Kfz.181 Tiger 1]" | "HULL MG34 [Sd.Kfz.181 Tiger 1]" | "MG 42 [Sd.Kfz 251 Half-track]";
  
  type RUS_ArmorWeapon = "19-K 45MM [BA-10]" | "COAXIAL DT [BA-10]" | "45MM M1937 [T70]" | "COAXIAL DT [T70]" | "76MM ZiS-5 [T34/76]" | "COAXIAL DT [T34/76]" | "HULL DT [T34/76]" | "D-5T 85MM [IS-1]" | "COAXIAL DT [IS-1]" | "HULL DT [IS-1]";
  
  type GB_ArmorWeapon = "QF 2-POUNDER [Daimler]" | "COAXIAL BESA [Daimler]" | "QF 2-POUNDER [Tetrarch]" | "COAXIAL BESA [Tetrarch]" | "37MM CANNON [M3 Stuart Honey]" | "COAXIAL M1919 [M3 Stuart Honey]" | "HULL M1919 [M3 Stuart Honey]" | "OQF 75MM [Cromwell]" | "COAXIAL BESA [Cromwell]" | "HULL BESA [Cromwell]" | "OQF 57MM [Crusader Mk.III]" | "COAXIAL BESA [Crusader Mk.III]" | "QF 17-POUNDER [Firefly]" | "COAXIAL M1919 [Firefly]" | "OQF 57MM [Churchill Mk.III]" | "COAXIAL BESA 7.92mm [Churchill Mk.III]" | "HULL BESA 7.92mm [Churchill Mk.III]" | "OQF 57MM [Churchill Mk.VII]" | "COAXIAL BESA 7.92mm [Churchill Mk.VII]" | "HULL BESA 7.92mm [Churchill Mk.VII]" | "OQF 75MM [Churchill Mk.VII]";
  
  type ArmorWeapon = US_ArmorWeapon | GER_ArmorWeapon | RUS_ArmorWeapon | GB_ArmorWeapon;
  
  // United States (US) Vehicles
  type US_Vehicle =
    | "M8 Greyhound"
    | "Stuart M5A1"
    | "Sherman M4A3(75)W"
    | "Sherman M4A3E2"
    | "Sherman M4A3E2(76)"
    | "M3 Half-track"
    | "GMC CCKW 353 (Transport)"
    | "GMC CCKW 353 (Supply)"
    | "Jeep Willys";
  
  // Germany (GER) Vehicles
  type GER_Vehicle =
    | "Sd.Kfz.234 Puma"
    | "Sd.Kfz.121 Luchs"
    | "Sd.Kfz.161 Panzer IV"
    | "Sd.Kfz.181 Tiger 1"
    | "Sd.Kfz.171 Panther"
    | "Sd.Kfz 251 Half-track"
    | "Opel Blitz (Transport)"
    | "Opel Blitz (Supply)"
    | "Kubelwagen";
  
  // Soviet Union (RUS) Vehicles
  type RUS_Vehicle =
    | "BA-10"
    | "T70"
    | "Tetrarch"
    | "IS-1"
    | "ZIS-5 (Transport)"
    | "ZIS-5 (Supply)"
    | "GAZ-67"
    | "M3 Half-track"
    | "T34/76"
  
  // Great Britain (GB) Vehicles
  type GB_Vehicle =
    | "Daimler"
    | "Tetrarch"
    | "M3 Stuart Honey"
    | "Cromwell"
    | "Crusader Mk.III"
    | "Firefly"
    | "Churchill Mk.III"
    | "Churchill Mk.VII"
    | "M3 Half-track"
    | "Bedford OYD (Transport)"
    | "Bedford OYD (Supply)"
    | "Jeep Willys";
  
  // Union of all Vehicle types
  type Vehicle = US_Vehicle | GER_Vehicle | RUS_Vehicle | GB_Vehicle;
  
  type CommanderAbility =
    | "BOMBING RUN"
    | "STRAFING RUN"
    | "PRECISION STRIKE"
  
  type WeaponCategory =
    | "Submachine Gun"
    | "Semi-Auto Rifle"
    | "Bolt-Action Rifle"
    | "Assault Rifle"
    | "Shotgun"
    | "Machine Gun"
    | "Sniper Rifle"
    | "Pistol"
    | "Flamethrower"
    | "Melee Weapon"
    | "Grenade"
    | "Satchel Charge"
    | "Anti-Personnel Mine"
    | "Anti-Tank Mine"
    | "Anti-Tank Rifle"
    | "Flare Gun"
    | "Artillery Gun"
    | "Anti-Tank Gun"
    | "Roadkill"
    | "Recon Vehicle"
    | "Light Tank"
    | "Medium Tank"
    | "Heavy Tank"
    | "Commander ability"
    | "Half-track"
    | "UNKNOWN"
  
  type Unknown = "UNKNOWN" | "Unknown"
  
  type Weapon = InfantryWeapon | Vehicle | ArmorWeapon | CommanderAbility | Unknown;
  
  type TeamsStats = {
    kills: number,
    deaths: number,
    weaponCategories: Partial<Record<WeaponCategory, number>>
    killsCategory: {
      infantry: number,
      armor: number,
      artillery: number,
      other: number,
    }
    points: {
      combat: number,
      support: number,
      offensive: number,
      defensive: number,
    }
    players: Player[]
  }
  
  export type MatchStats = {
    allies: TeamsStats
    axis: TeamsStats
    weapons: Partial<Record<Weapon, number>>
  }

  export type Faceoff = {
    name: string
    kills: number
    deaths: number
    diff: number
}