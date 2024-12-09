type Team = 'allies' | 'axis'
type Nation = 'us' | 'gb' | 'ger' | 'rus'
type MapEnvironment = 'day' | 'night' | 'dusk' | 'rain' | 'dawn' | 'overcast'
export type GameMode = 'warfare' | 'offensive' | 'skirmish' | 'control'

export type MapTeam = {
  name: Nation
  team: Team
}

export interface MapLayer {
  id: string
  map: Map
  game_mode: GameMode
  attackers: Team | null
  environment: MapEnvironment
  pretty_name: string
  image_name: string
}

export interface Map {
  id: string
  name: string
  tag: string
  pretty_name: string
  shortname: string
  allies: MapTeam
  axis: MapTeam
}
