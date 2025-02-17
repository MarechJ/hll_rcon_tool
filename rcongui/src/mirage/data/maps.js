export const MAPS = {
  carentan: {
    name: "Carentan",
    maxPlayers: 100,
    gameMode: "warfare",
    country: "FR",
    weather: ["clear", "fog", "rain"],
    time: ["day", "night", "dawn", "dusk"]
  },
  kursk: {
    name: "Kursk",
    maxPlayers: 100,
    gameMode: "warfare",
    country: "RU",
    weather: ["clear", "fog"],
    time: ["day", "dawn", "dusk"]
  },
  stalingrad: {
    name: "Stalingrad",
    maxPlayers: 100,
    gameMode: ["warfare", "offensive"],
    country: "RU",
    weather: ["clear", "snow"],
    time: ["day", "night"]
  },
  omaha: {
    name: "Omaha Beach",
    maxPlayers: 100,
    gameMode: "offensive",
    country: "FR",
    weather: ["clear", "fog", "rain"],
    time: ["dawn"]
  }
};

export const MAP_ROTATION = [
  { map: "carentan", mode: "warfare" },
  { map: "kursk", mode: "warfare" },
  { map: "stalingrad", mode: "warfare" },
  { map: "omaha", mode: "offensive" },
  { map: "stalingrad", mode: "offensive" }
]; 