import { PlayerDetailDrawer } from "@/components/PlayerProfileDrawer";
import { cmd } from "@/utils/fetchUtils";
import React, { useEffect, useMemo } from "react";
import { useGlobalStore } from "./useGlobalState";
import dayjs from "dayjs";

export const SidebarContext = React.createContext();

export const PlayerSidebarProvider = ({ children }) => {
  const [open, setOpen] = React.useState(false);
  const [player, setPlayer] = React.useState(null);
  const [playerId, setPlayerId] = React.useState("");
  const [isFetching, setIsFetching] = React.useState(false);
  const serverStatus = useGlobalStore((state) => state.status);
  const onlinePlayers = useGlobalStore((state) => state.onlinePlayers);

  useEffect(() => {
    const getPlayer = async () => {
      if (!playerId) return;
      setOpen(true);
      setIsFetching(true);
      const player = await cmd.GET_PLAYER({ params: { player_id: playerId } });
      if (player) {
        setPlayer({
          ...player,
          isOnline: onlinePlayers.some(
            (aPlayer) => aPlayer.player_id === player.player_id
          ),
        });
        setIsFetching(false);
      } else {
        setTimeout(() => {
          setPlayer(null);
          setIsFetching(false);
        }, 2000);
      }
    };
    getPlayer();
  }, [playerId]);
/*
[
    {
        "server_number": 2,
        "expiration": "2024-10-19T13:47:06+00:00"
    },
    {
        "server_number": 1,
        "expiration": "3000-01-01T00:00:00+00:00"
    }
]
*/
  const extendedPlayer = useMemo(() => {
    let is_online = false;
    let is_vip = false;
    if (player && onlinePlayers.length) {
      // check online status
      if (
        onlinePlayers.some((aPlayer) => aPlayer.player_id === player.player_id)
      ) {
        is_online = true;
      }
      // check vip status
      if (player?.profile?.vips?.length) {
        const vip = player.profile.vips.find(vip => vip.server_number === serverStatus?.server_number);
        if (vip && dayjs().isBefore(vip.expiration)) {
          is_vip = true;
        }
      }

      return {
        ...player,
        is_online,
        is_vip,
      };
    }
    return player;
  }, [player, onlinePlayers, serverStatus]);

  const contextValue = React.useMemo(
    () => ({
      open,
      setOpen,
      player: extendedPlayer,
      setPlayer,
      playerId,
      setPlayerId,
      isFetching,
      setIsFetching,
    }),
    [open, player, playerId, isFetching]
  );

  return (
    <SidebarContext.Provider value={contextValue}>
      {children}
      <PlayerDetailDrawer />
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
      setIsFetching: () => {},
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
