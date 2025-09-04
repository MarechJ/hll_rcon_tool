import { cmd } from "@/utils/fetchUtils";
import { queryOptions } from "@tanstack/react-query";

// Define query keys to maintain consistent query identifiers
export const mapsManagerQueryKeys = {
  currentMap: [{ queryIdentifier: "get_map" }],
  maps: [{ queryIdentifier: "get_maps" }],
  mapRotation: [{ queryIdentifier: "get_map_rotation" }],
  mapRotationShuffle: [{ queryIdentifier: "get_map_rotation_shuffle" }],
  gameState: [{ queryIdentifier: "get_gamestate" }],
  votemapStatus: [{ queryIdentifier: "get_votemap_status" }],
  voteMapConfig: [{ queryIdentifier: "get_votemap_config" }],
  votemapWhitelist: [{ queryIdentifier: "get_votemap_whitelist" }],
  objectives: [{ queryIdentifier: "get_objective_rows" }],
};

// Define query options for fetching data
export const mapsManagerQueryOptions = {
  currentMap: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.currentMap,
      queryFn: cmd.GET_CURRENT_MAP,
    }),
  // Get all available maps
  maps: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.maps,
      queryFn: cmd.GET_MAPS,
    }),

  // Get current map rotation
  mapRotation: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.mapRotation,
      queryFn: cmd.GET_MAP_ROTATION,
    }),

  // Get map rotation shuffle config
  mapRotationShuffle: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.mapRotationShuffle,
      queryFn: cmd.GET_MAP_ROTATION_SHUFFLE,
    }),

  // Get current game state
  gameState: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.gameState,
      queryFn: cmd.GET_GAME_STATE,
      refetchInterval: 60000, // Refetch every minute
    }),

  votemapStatus: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.votemapStatus,
      queryFn: async () => {
        const updated = new Date()
        const res = await cmd.GET_VOTEMAP_STATUS()
        return {
          ...res,
          updated,
        }
      },
    }),

  // Get current votemap configuration
  voteMapConfig: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.voteMapConfig,
      queryFn: cmd.GET_VOTEMAP_CONFIG,
    }),

  votemapWhitelist: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.votemapWhitelist,
      queryFn: cmd.GET_VOTEMAP_WHITELIST,
    }),

  objectives: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.objectives,
      queryFn: cmd.GET_MAP_OBJECTIVES,
    }),
};

// Define mutation options for updating data
export const mapsManagerMutationOptions = {
  // Set map rotation
  setMapRotation: {
    mutationFn: (mapNames) =>
      cmd.SET_MAP_ROTATION({
        payload: { map_names: mapNames },
        throwRouteError: false,
      }),
  },

  // Change current map
  changeMap: {
    mutationFn: ({ mapId, mapOrdinal = 1 }) =>
      cmd.SET_MAP({ payload: { map_name: mapId, map_ordinal: mapOrdinal }, throwRouteError: false }),
  },

  // Set map rotation shuffle
  setMapRotationShuffle: {
    mutationFn: (enabled) =>
      cmd.SET_MAP_ROTATION_SHUFFLE({
        payload: { enabled },
        throwRouteError: false,
      }),
  },

  // Set map objectives
  changeObjectives: {
    mutationFn: ({ objectives, random_constraints }) =>
      cmd.SET_MAP_OBJECTIVES({
        payload: { objectives, random_constraints },
        throwRouteError: false,
      }),
  },

  resetVotemapState: {
    mutationFn: () =>
      cmd.RESET_VOTEMAP_STATE({
        throwRouteError: false,
      }),
  },

  resetVotemapWhitelist: {
    mutationFn: () =>
      cmd.RESET_VOTEMAP_WHITELIST({
        throwRouteError: false,
      }),
  },

  setVotemapConfig: {
    mutationFn: (config) =>
      cmd.SET_VOTEMAP_CONFIG({
        payload: config,
        throwRouteError: false,
      }),
  },

  setWhitelist: {
    mutationFn: (whitelist) =>
      cmd.SET_VOTEMAP_WHITELIST({
        payload: { map_names: whitelist },
        throwRouteError: false,
      }),
  },

  sendVotemapReminder: {
    mutationFn: () => cmd.SEND_VOTEMAP_REMINDER({ throwRouteError: false }),
  },
};
