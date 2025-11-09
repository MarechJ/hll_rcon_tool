import { teamsLiveQueryOptions } from "@/queries/teams-live-query";
import { cmd } from "@/utils/fetchUtils";
import { queryOptions, useQueries, useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { create } from "zustand";

// Create the Zustand store
export const useGlobalStore = create((set) => ({
  // State
  serverState: null,
  status: null,
  servers: [],
  gameState: null,
  onlineIngameMods: [],
  onlineCrconMods: [],
  onlinePlayers: [],
  // Actions to update state
  updateStatus: (data) => set(() => ({ status: data })),
  updateServerState: (data) => set(() => ({ serverState: data })),
  updateServers: (data) => set(() => ({ servers: data })),
  updateGameState: (data) => set(() => ({ gameState: data })),
  updateOnlineIngameMods: (data) => set(() => ({ onlineIngameMods: data })),
  updateOnlineCrconMods: (data) => set(() => ({ onlineCrconMods: data })),
  updateOnlinePlayers: (data) => set(() => ({ onlinePlayers: data })),
}));

const staleTime = 15 * 1000;
const refetchInterval = 30 * 1000;

// Define your global queries with onSuccess callbacks
const globalQueries = [
  queryOptions({
    queryKey: [{ queryIdentifier: "get_status" }],
    queryFn: cmd.GET_GAME_SERVER_STATUS,
    select: (data) => {
      useGlobalStore.setState({ status: data });
      return data;
    },
  }),
  queryOptions({
    queryKey: [{ queryIdentifier: "get_gamestate" }],
    queryFn: cmd.GET_GAME_STATE,
    select: (data) => {
      useGlobalStore.setState({ gameState: data });
      return data;
    },
  }),
  queryOptions({
    queryKey: [{ queryIdentifier: "get_server_list" }],
    queryFn: () => cmd.GET_GAME_SERVER_LIST({ params: { include_current: 'true' } }),
    select: (data) => {
      const currentServer = data.find(server => server.current === true) || null;
      const otherServers = data.filter(server => server.current !== true);

      useGlobalStore.setState({
        serverState: currentServer,
        servers: otherServers
      });

      return data;
    },
  }),
  queryOptions({
    queryKey: [{ queryIdentifier: "get_ingame_mods" }],
    queryFn: cmd.GET_INGAME_MODS,
    select: (data) => {
      useGlobalStore.setState({ onlineIngameMods: data });
      return data;
    },
  }),
  queryOptions({
    queryKey: [{ queryIdentifier: "get_online_mods" }],
    queryFn: cmd.GET_CRCON_MODS,
    select: (data) => {
      useGlobalStore.setState({ onlineCrconMods: data });
      return data;
    },
  }),
  teamsLiveQueryOptions,
];

export const GlobalState = () => {
  const { isSuccess: isCrconConnected } = useQuery({
    queryKey: [{ queryIdentifier: "get_connection_info" }],
    queryFn: cmd.GET_CRCON_SERVER_CONNECTION,
    refetchInterval,
    retry: 1,
  });

  useQueries({
    queries: globalQueries.map((query) =>
      queryOptions({
        staleTime,
        refetchInterval,
        enabled: isCrconConnected,
        ...query,
      })
    ),
  });

  return null;
};