import { teamsLiveQueryOptions } from "@/queries/teams-live-query";
import { cmd } from "@/utils/fetchUtils";
import { useQueries, useQuery } from "@tanstack/react-query";
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
  {
    queryKey: ["server", "state"],
    queryFn: cmd.GET_GAME_SERVER_STATUS,
    select: (data) => {
      useGlobalStore.setState((state) => ({ status: data }));
      return data;
    },
  },
  {
    queryKey: ["game", "state"],
    queryFn: cmd.GET_GAME_STATE,
    select: (data) => {
      useGlobalStore.setState((state) => ({ gameState: data }));
      return data;
    },
  },
  {
    queryKey: ["server", "list"],
    queryFn: cmd.GET_GAME_SERVER_LIST,
    select: (data) => {
      useGlobalStore.setState((state) => ({ servers: data }));
      return data;
    },
  },
  {
    queryKey: ["ingame-mods", "live"],
    queryFn: cmd.GET_INGAME_MODS,
    select: (data) => {
      useGlobalStore.setState((state) => ({ onlineIngameMods: data }));
      return data;
    },
  },
  {
    queryKey: ["crcon-mods", "live"],
    queryFn: cmd.GET_CRCON_MODS,
    select: (data) => {
      useGlobalStore.setState((state) => ({ onlineCrconMods: data }));
      return data;
    },
  },
  teamsLiveQueryOptions,
];

export const GlobalState = () => {
  const { data, isSuccess: isCrconConnected } = useQuery({
    queryKey: ["crcon", "state"],
    queryFn: cmd.GET_CRCON_SERVER_CONNECTION,
    refetchInterval,
    retry: 1,
  });

  useEffect(() => {
    if (isCrconConnected) {
      useGlobalStore.setState({ serverState: data });
    } else {
      useGlobalStore.setState({ serverState: null });
    }
  }, [isCrconConnected]);

  useQueries({
    queries: globalQueries.map((query) => ({
      staleTime,
      refetchInterval,
      enabled: isCrconConnected,
      ...query,
    })),
  });

  return null;
}; 