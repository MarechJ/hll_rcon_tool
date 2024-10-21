import { PlayerDetailDrawer } from "@/components/PlayerProfileDrawer";
import { cmd } from "@/utils/fetchUtils";
import React, { useEffect, useMemo } from "react";
import { useGlobalStore } from "./useGlobalState";
import dayjs from "dayjs";
import { useQuery } from "@tanstack/react-query";

export const SidebarContext = React.createContext();

export const PlayerSidebarProvider = ({ children }) => {
  const [open, setOpen] = React.useState(false);
  const [player, setPlayer] = React.useState(null);
  const [playerId, setPlayerId] = React.useState("");
  const serverStatus = useGlobalStore((state) => state.status);
  const onlinePlayers = useGlobalStore((state) => state.onlinePlayers);

  const { data: comments } = useQuery({
    queryKey: ["player", "comments", player?.player_id ?? playerId],
    queryFn: () =>
      cmd.GET_PLAYER_COMMENTS({
        params: { player_id: player?.player_id ?? playerId },
      }),
    enabled: open && (!!playerId || !!player?.player_id),
    refetchInterval: 15 * 1000,
    initialData: [],
  });

  console.log({ enabled: open && (!!playerId || !!player?.player_id) });

  const { data: profile, isFetching } = useQuery({
    queryKey: ["player", "profile", playerId],
    queryFn: () => cmd.GET_PLAYER({ params: { player_id: playerId } }),
    enabled: open && !!playerId,
    refetchOnWindowFocus: false,
  });

  const handleSetId = (id) => {
    if (!id) return;
    setOpen(true);
    setPlayerId(id);
  };

  const handleSetPlayer = (player) => {
    if (!player) return;
    setOpen(true);
    setPlayer(player);
  };

  const extendedPlayer = useMemo(() => {
    if (!open) return null;

    let finalPlayer;

    // if player object set
    if (player) {
      // find it in online players
      finalPlayer = onlinePlayers.find(
        (aPlayer) => aPlayer.player_id === player.player_id
      );
      if (finalPlayer) {
        finalPlayer.in_online = true;
      } else {
        // or set to the player if not online
        finalPlayer = { ...player };
        finalPlayer.is_online = false;
      }
    }

    if (!finalPlayer && profile) {
      finalPlayer = onlinePlayers.find(
        (aPlayer) => aPlayer.player_id === profile.player_id
      );
      if (finalPlayer) {
        finalPlayer.in_online = true;
      } else {
        // or set to the player if not online
        finalPlayer = {
          profile,
          is_online: false,
          is_vip: false,
        };
        const vip = profile.vips.find(
          (vip) => vip.server_number === serverStatus?.server_number
        );
        if (vip && dayjs().isBefore(vip.expiration)) {
          is_vip = true;
        }
      }
    }

    if (finalPlayer) {
      finalPlayer.comments = comments;
      return finalPlayer;
    }

    return null;
  }, [player, onlinePlayers, serverStatus, comments, profile, playerId]);

  const contextValue = React.useMemo(
    () => ({
      open,
      setOpen,
      player: extendedPlayer,
      setPlayer: handleSetPlayer,
      playerId,
      setPlayerId: handleSetId,
      isFetching,
    }),
    [open, player, playerId, isFetching]
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
      setOpen: () => {},
      player: null,
      setPlayer: () => {},
      playerId: null,
      setPlayerId: () => {},
      isFetching: false,
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
