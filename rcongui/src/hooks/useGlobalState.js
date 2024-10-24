import { extractPlayers } from "@/utils/extractPlayers";
import { cmd } from "@/utils/fetchUtils";
import { useQueries } from "@tanstack/react-query";
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
    queryKey: ["crcon", "state"],
    queryFn: cmd.GET_STATUS,
    select: (data) => {
      useGlobalStore.setState((state) => ({ status: data }));
      return data;
    },
  },
  {
    queryKey: ["server", "state"],
    queryFn: cmd.GET_GAME_SERVER_CONNECTION,
    select: (data) => {
      useGlobalStore.setState((state) => ({ serverState: data }));
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
  {
    queryKey: ["teams", "live"],
    queryFn: cmd.GET_LIVE_TEAMS,
    select: (data) => {
      useGlobalStore.setState((state) => ({ onlinePlayers: extractPlayers(data) }));
      return data;
    },
  },
];

export const GlobalState = () => {
  // Use React Query's `useQueries` to fetch multiple pieces of data
  const results = useQueries({
    queries: globalQueries.map((query) => ({
      ...query,
      staleTime,
      // only refetch if the query is stale and does not have an error
      refetchInterval: (query) => query.state.error ? false : refetchInterval,
    })),
  });

  return null; // This component only updates the Zustand store, no UI rendering needed
};
