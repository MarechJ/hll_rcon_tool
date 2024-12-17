import { PlayerDetailDrawer } from "@/components/PlayerProfileDrawer";
import { cmd } from "@/utils/fetchUtils";
import {createContext, useContext, useMemo, useState} from "react";
import { useGlobalStore } from "./useGlobalState";
import dayjs from "dayjs";
import { useQuery } from "@tanstack/react-query";
import { playerProfileQueryOptions } from "@/queries/player-profile-query";

/**
 * @typedef {Object} PlayerVIP
 * @property {number} server_number - The server number where the VIP status applies
 * @property {string} expiration - The expiration date of the VIP status
 */

/**
 * @typedef {Object} PlayerProfile
 * @property {string} player_id - Unique identifier for the player
 * @property {Array<{name: string}>} names - Array of player names
 * @property {PlayerVIP[]} vips - Array of VIP statuses across different servers
 */

/**
 * @typedef {Object} Player
 * @property {string} player_id - Unique identifier for the player
 * @property {string} name - Current display name of the player
 * @property {boolean} is_online - Whether the player is currently online
 * @property {boolean} [is_banned] - Whether the player is currently banned
 * @property {boolean} [is_vip] - Whether the player has VIP status
 * @property {PlayerVIP} [vip] - VIP details if the player is a VIP
 * @property {PlayerProfile} profile - Player's profile information
 * @property {Array<Object>} messages - Player's message history
 * @property {Array<Object>} comments - Comments about the player
 * @property {Array<Object>} bans - Player's ban history
 */

export const SidebarContext = createContext();

export const PlayerSidebarProvider = ({ children }) => {
  const [open, setOpen] = useState(false);
  const [playerId, setPlayerId] = useState("");
  const serverStatus = useGlobalStore((state) => state.status);
  const onlinePlayers = useGlobalStore((state) => state.onlinePlayers);
  const enabled = open && !!playerId;
  const staleTime = 60 * 1000; // 60 seconds

  const {
    data: comments,
    isLoading: isLoadingComments,
    error: commentsError,
  } = useQuery({
    queryKey: ["player", "comments", playerId],
    queryFn: () =>
      cmd.GET_PLAYER_COMMENTS({
        params: { player_id: playerId },
        throwRouteError: false,
      }),
    enabled,
    staleTime,
    refetchOnWindowFocus: false,
    refetchInterval: (query) => {
      // Only refetch if the data is stale and there's no error
      return query.state.isStale && !query.state.error ? staleTime : false;
    },
  });

  const {
    data: bans,
    isLoading: isLoadingBans,
    error: bansError,
  } = useQuery({
    queryKey: ["player", "bans", playerId],
    queryFn: () =>
      cmd.GET_PLAYER_BANS({
        params: { player_id: playerId },
        throwRouteError: false,
      }),
    enabled,
    staleTime,
    refetchOnWindowFocus: false,
    refetchInterval: (query) => {
      // Only refetch if the data is stale and there's no error
      return query.state.isStale && !query.state.error ? staleTime : false;
    },
  });

  const {
    data: messages,
    isLoading: isLoadingMessages,
    error: messagesError,
  } = useQuery({
    queryKey: ["player", "messages", playerId],
    queryFn: () =>
      cmd.GET_PLAYER_MESSAGES({
        params: { player_id: playerId },
        throwRouteError: false,
      }),
    enabled,
    staleTime,
    refetchOnWindowFocus: false,
    refetchInterval: (query) => {
      // Only refetch if the data is stale and there's no error
      return query.state.isStale && !query.state.error ? staleTime : false;
    },
  });

  const {
    data: profile,
    isLoading: isLoadingProfile,
    error: profileError,
  } = useQuery({
    ...playerProfileQueryOptions(playerId, { throwRouteError: false }),
    enabled,
    staleTime,
    refetchOnWindowFocus: false,
    refetchInterval: (query) => {
      // Only refetch if the data is stale and there's no error
      return query.state.isStale && !query.state.error ? staleTime : false;
    },
  });

  const handleSetId = (id) => {
    if (!id) return;
    setOpen(true);
    setPlayerId(id);
  };

  const handleClose = () => {
    setOpen(false);
    setPlayerId("");
  };

  const handleSwitchPlayer = (id) => {
    setPlayerId(id);
  };

  const player = useMemo(() => {
    if (!open || !playerId) return null;

    const getOnlinePlayer = (id) =>
      onlinePlayers.find((p) => p.player_id === id);

    const getPlayerWithOnlineStatus = (player, isOnline) => ({
      ...player,
      is_online: isOnline,
    });

    let aPlayer = getOnlinePlayer(playerId);

    if (aPlayer) {
      aPlayer = getPlayerWithOnlineStatus(aPlayer, true);
    } else if (profile) {
      aPlayer = getPlayerWithOnlineStatus({ profile }, false);
    } else {
      return null;
    }
    
    aPlayer.messages = messages ?? [];
    aPlayer.comments = comments ?? [];
    aPlayer.bans = bans ?? [];
    if (aPlayer.bans.length > 0) {
      aPlayer.is_banned = true;
    }

    const vip = aPlayer.profile.vips.find(
      (v) => v.server_number === serverStatus?.server_number
    );
    if (vip && dayjs().isBefore(vip.expiration)) {
      aPlayer.is_vip = true;
      aPlayer.vip = vip;
    }

    aPlayer.player_id = aPlayer.player_id ?? aPlayer.profile.player_id;
    aPlayer.name = aPlayer.name ?? aPlayer.profile.names[0]?.name;

    return aPlayer;
  }, [open, playerId, onlinePlayers, serverStatus, comments, bans, profile, messages]);

  const isLoading = isLoadingComments || isLoadingBans || isLoadingProfile || isLoadingMessages;

  const contextValue = useMemo(
    () => ({
      open,
      close: handleClose,
      player,
      openWithId: handleSetId,
      switchPlayer: handleSwitchPlayer,
      isLoading,
      commentsError,
      bansError,
      profileError,
      messagesError,
    }),
    [open, player, playerId, isLoading, commentsError, bansError, profileError, messagesError]
  );

  return (
    <SidebarContext.Provider value={contextValue}>
      {children}
      {open && <PlayerDetailDrawer />}
    </SidebarContext.Provider>
  );
};

export const usePlayerSidebar = () => {
  const context = useContext(SidebarContext);

  if (!context && process.env.NODE_ENV === "development") {
    // In development, return a fallback or log a warning instead of throwing an error
    console.warn(
      "usePlayerSidebar must be used within an PlayerSidebarProvider"
    );
    return {
      open: false,
      close: () => {},
      player: null,
      openWithId: () => {},
      switchPlayer: () => {},
      isLoading: false,
      commentsError: null,
      bansError: null,
      profileError: null,
      messagesError: null,
    };
  }

  // Check if context is undefined, indicating it was used outside of a provider
  if (!context) {
    throw new Error(
      "usePlayerSidebar must be used within an PlayerSidebarProvider"
    );
  }
  return context;
};
