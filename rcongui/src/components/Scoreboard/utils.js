export const UNKNOWN_MAP_NAME = 'unknown';


export const SKIRMISH_TAG_LOOKUP = new Map([
  ['ELA', 'elalamein'],
  ['DRL', 'driel'],
])

export const map_to_pict = new Map([
  ["carentan", "/maps/carentan.webp"],
  ["carentan_night", "/maps/carentan-night.webp"],
  ["driel", "/maps/driel.webp"],
  ["driel skirmish", "/maps/driel.webp"],
  ["driel_night", "/maps/driel-night.webp"],
  ["driel skirmish night", "/maps/driel-night.webp"],
  ["elalamein", "/maps/elalamein.webp"],
  ["elalamein skirmish", "/maps/elalamein.webp"],
  ["elalamein_night", "/maps/elalamein-night.webp"],
  ["elalamein skirmish night", "/maps/elalamein-night.webp"],
  ["foy", "/maps/foy.webp"],
  ["foy_night", "/maps/foy-night.webp"],
  ["hill400", "/maps/hill400.webp"],
  ["hill400_night", "/maps/hill400-night.webp"],
  ["hurtgenforest", "/maps/hurtgen.webp"],
  ["hurtgenforest_night", "/maps/hurtgen-night.webp"],
  ["kharkov", "/maps/kharkov.webp"],
  ["kharkov_night", "/maps/kharkov-night.webp"],
  ["kursk", "/maps/kursk.webp"],
  ["kursk_night", "/maps/kursk-night.webp"],
  ["omahabeach", "/maps/omaha.webp"],
  ["omahabeach_night", "/maps/omaha-night.webp"],
  ["purpleheartlane", "/maps/phl.webp"],
  ["purpleheartlane_night", "/maps/phl-night.webp"],
  ["remagen", "/maps/remagen.webp"],
  ["remagen_night", "/maps/remagen-night.webp"],
  ["stalingrad", "/maps/stalingrad.webp"],
  ["stalingrad_night", "/maps/stalingrad-night.webp"],
  ["stmariedumont", "/maps/smdm.webp"],
  ["stmariedumont_night", "/maps/smdm-night.webp"],
  ["stmereeglise", "/maps/sme.webp"],
  ["stmereeglise_night", "/maps/sme-night.webp"],
  ["utahbeach", "/maps/utah.webp"],
  ["utahbeach_night", "/maps/utah-night.webp"],
  [UNKNOWN_MAP_NAME, "/maps/unknown.webp"],
]);

export const getMapName = (mapName) => {
  if (mapName === undefined) {
    return UNKNOWN_MAP_NAME;
  }


  const parts = mapName.split("_");
  if (parts && SKIRMISH_TAG_LOOKUP.get(parts[0])) {
    let base_name = SKIRMISH_TAG_LOOKUP.get(parts[0])
    if (mapName.toLowerCase().search('night') !== -1) {
      return base_name + ' skirmish' + ' night'
    } else {
      return base_name + ' skirmish'
    }
  }
  else if (parts && parts.length > 0) {
    if (parts.at(-1).toLowerCase() == "night") {
      return parts[0] + "_night"
    } else {
      return parts[0];
    }
  }

  return UNKNOWN_MAP_NAME;
};

export const getMapImageUrl = (mapName) => {
  const imageName = map_to_pict.get(getMapName(mapName))

  if (imageName === undefined) {
    return map_to_pict.get(UNKNOWN_MAP_NAME)
  } else {
    return imageName
  }
}