export interface MapMode {
    id:          string;
    map:         Map;
    game_mode:   GameMode;
    attackers:   Team | null;
    environment: MapEnvironment;
    pretty_name: string;
    image_name:  string;
}

export interface Map {
    id:          string;
    name:        string;
    tag:         string;
    pretty_name: string;
    shortname:   string;
    allies:      MapTeam;
    axis:        MapTeam;
}

export type Team = "allies" | "axis";
export type Nation = "us" | "gb" | "ger" | "rus";
export type GameMode = "warfare" | "offensive" | "skirmish";
export type MapEnvironment = "day" | "night" | "dusk" | "rain";

export interface MapTeam {
    name: Nation;
    team: Team;
}
