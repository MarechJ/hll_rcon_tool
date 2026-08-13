"""HLL Vietnam map data.

The catalog is intentionally isolated even while it only contains the unknown
fallback. Known HLLV maps and layers can be added here without changing shared
RCON command code or risking a lookup in the WW2 catalog.
"""

import hllrcon

from rcon.maps import (
    UNKNOWN_MAP_NAME,
    Environment,
    Faction,
    GameMode,
    Layer,
    Map,
    Orientation,
    Team,
    is_server_loading_map,
)

HLLV_MAPS: dict[str, Map] = {
    UNKNOWN_MAP_NAME: Map(
        id=UNKNOWN_MAP_NAME,
        name=UNKNOWN_MAP_NAME,
        tag="",
        pretty_name=UNKNOWN_MAP_NAME,
        shortname=UNKNOWN_MAP_NAME,
        allies=Faction(name=UNKNOWN_MAP_NAME, team=Team.ALLIES),
        axis=Faction(name=UNKNOWN_MAP_NAME, team=Team.AXIS),
        orientation=Orientation.VERTICAL,
    )
}
for map_data in hllrcon.HLLVMap.all():
    map_ = Map.from_hllrcon(map_data)
    HLLV_MAPS[map_.id] = map_

HLLV_LAYERS: dict[str, Layer] = {
    UNKNOWN_MAP_NAME: Layer(
        id=UNKNOWN_MAP_NAME,
        map=HLLV_MAPS[UNKNOWN_MAP_NAME],
        game_mode=GameMode.DOMINATION,
    )
}
# TODO: hllrcon does not preserve details of outdated map IDs. CRCON on the other hand needs them for historical data purposes.
#   If a layer is ever removed or has its ID updated, its details will have to be manually added above.
for layer_data in hllrcon.HLLVLayer.all():
    layer = Layer.from_hllrcon(layer_data)
    HLLV_LAYERS[layer.id] = layer

def parse_layer(layer_name: str | Layer) -> Layer:
    if isinstance(layer_name, Layer):
        return layer_name
    if is_server_loading_map(layer_name):
        return HLLV_LAYERS[UNKNOWN_MAP_NAME]

    layer = HLLV_LAYERS.get(layer_name.lower())
    if layer is not None:
        return layer

    game_mode = GameMode.DOMINATION

    # Preserve the server identifier until its full reference data is added.
    # Most importantly, do not fall back to the HLL/WW2 layer registry.
    return Layer(
        id=layer_name,
        map=HLLV_MAPS[UNKNOWN_MAP_NAME],
        game_mode=game_mode,
        environment=Environment.DAY,
    )
