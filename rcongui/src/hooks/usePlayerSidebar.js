import { PlayerDetailDrawer } from "@/components/PlayerProfileDrawer";
import { cmd } from "@/utils/fetchUtils";
import React, { useEffect } from "react";

export const SidebarContext = React.createContext();

// TODO
// Make this fetch the player's data based on playerId
// Introduce loading state so the sidebar does not open until some data are present
// It should update the player's data periodically including comments etc
export const PlayerSidebarProvider = ({ children }) => {
  const [open, setOpen] = React.useState(false);
  const [player, setPlayer] = React.useState(null);
  const [playerId, setPlayerId] = React.useState("");
  const [isFetching, setIsFetching] = React.useState(false);

  // 1. Set Steam ID
  // 2. useInterval to get_player
  // 3. Open sidebar with loading state
  //    - Use loading state inside the sidebar to create Skeleton UI
  // 4. On loaded data, set player state and set loading state to false
  useEffect(() => {
    const getPlayer = async () => {
      if (!playerId) return;
      setOpen(true);
      setIsFetching(true);
      const player = await cmd.GET_PLAYER({ player_id: playerId });
      if (player) {
        setPlayer(player);
        setIsFetching(false);
      } else {
        setTimeout(() => {
          setPlayer(null)
          setIsFetching(false);
        }, 2000);
      }
    };
    getPlayer();
  }, [playerId]);

  const contextValue = React.useMemo(
    () => ({
      open,
      setOpen,
      player,
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
