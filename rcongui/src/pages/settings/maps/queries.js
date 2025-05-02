import { cmd, get, postData } from "@/utils/fetchUtils";
import { queryOptions } from "@tanstack/react-query";

// Define query keys to maintain consistent query identifiers
export const mapsManagerQueryKeys = {
  maps: [{ queryIdentifier: "get_maps" }],
  mapRotation: [{ queryIdentifier: "get_map_rotation" }],
  gameState: [{ queryIdentifier: "get_gamestate" }],
  voteMapConfig: [{ queryIdentifier: "get_votemap_config" }],
};

// Define query options for fetching data
export const mapsManagerQueryOptions = {
  // Get all available maps
  maps: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.maps,
      queryFn: async () => {
        const response = await get("get_maps");
        const data = await response.json();
        return data.result || [];
      },
      refetchInterval: 60000, // Refetch every minute
    }),

  // Get current map rotation
  mapRotation: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.mapRotation,
      queryFn: async () => {
        const response = await get("get_map_rotation");
        const data = await response.json();
        return data.result || [];
      },
    }),

  // Get current game state
  gameState: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.gameState,
      queryFn: async () => {
        return await cmd.GET_GAMESTATE();
      },
      refetchInterval: 60000, // Refetch every minute
    }),

  // Get current votemap configuration
  voteMapConfig: () =>
    queryOptions({
      queryKey: mapsManagerQueryKeys.voteMapConfig,
      queryFn: async () => {
        const response = await get("get_votemap_config");
        const data = await response.json();
        return data.result || {};
      },
      refetchInterval: 10000, // Refetch every 10 seconds
    }),
};

// Define mutation options for updating data
export const mapsManagerMutationOptions = {
  // Set map rotation
  setMapRotation: {
    mutationFn: async (mapNames) => {
      const response = await postData(`${process.env.REACT_APP_API_URL}set_maprotation`, {
        map_names: mapNames,
      });
      return response;
    },
  },

  // Change current map
  changeMap: {
    mutationFn: async (mapName) => {
      const response = await postData(`${process.env.REACT_APP_API_URL}change_map`, {
        map_name: mapName,
      });
      return response;
    },
  },
}; 