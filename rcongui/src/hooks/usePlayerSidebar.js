import { PlayerDetailDrawer } from "@/components/PlayerProfileDrawer";
import { cmd } from "@/utils/fetchUtils";
import React, { useEffect, useMemo } from "react";
import { useGlobalStore } from "./useGlobalState";
import dayjs from "dayjs";
import { useQuery } from "@tanstack/react-query";
import { playerProfileQueryOptions } from "@/queries/player-profile-query";

export const SidebarContext = React.createContext();

export const PlayerSidebarProvider = ({ children }) => {
  const [open, setOpen] = React.useState(false);
  const [playerId, setPlayerId] = React.useState("");
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

  console.log(isLoadingComments, comments);

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

    aPlayer.comments = comments;
    aPlayer.bans = bans;
    if (bans.length > 0) {
      aPlayer.is_banned = true;
    }

    const vip = aPlayer.profile.vips.find(
      (v) => v.server_number === serverStatus?.server_number
    );
    if (vip && dayjs().isBefore(vip.expiration)) {
      aPlayer.is_vip = true;
      aPlayer.vip = vip;
    }

    aPlayer.messages = messages;
    aPlayer.player_id = aPlayer.player_id ?? aPlayer.profile.player_id;
    aPlayer.name = aPlayer.name ?? aPlayer.profile.names[0]?.name;

    return aPlayer;
  }, [open, playerId, onlinePlayers, serverStatus, comments, bans, profile, messages]);

  const isLoading = isLoadingComments || isLoadingBans || isLoadingProfile || isLoadingMessages;

  const contextValue = React.useMemo(
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
  const context = React.useContext(SidebarContext);

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
