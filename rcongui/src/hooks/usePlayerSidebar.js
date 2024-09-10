import { PlayerDetailDrawer } from '@/components/PlayerProfileDrawer';
import React from 'react';

export const SidebarContext = React.createContext();

// TODO
// Make this fetch the player's data based on playerId
// Introduce loading state so the sidebar does not open until some data are present
// It should update the player's data periodically including comments etc
export const PlayerSidebarProvider = ({ children }) => {
  const [open, setOpen] = React.useState(false);
  const [player, setPlayer] = React.useState(null);
  const [playerId, setPlayerId] = React.useState('');

  // 1. Set Steam ID
  // 2. useInterval to get_player
  // 3. Open sidebar with loading state
  //    - Use loading state inside the sidebar to create Skeleton UI
  // 4. On loaded data, set player state and set loading state to false 

  const contextValue = React.useMemo(() => ({
    open, setOpen, player, setPlayer, playerId, setPlayerId
}), [open, player, playerId]);

  return (
    <SidebarContext.Provider value={contextValue}>
      {children}
      <PlayerDetailDrawer />
    </SidebarContext.Provider>
  );
};

export const usePlayerSidebar = () => {
  const context = React.useContext(SidebarContext);

  if (!context && process.env.NODE_ENV === 'development') {
      // In development, return a fallback or log a warning instead of throwing an error
      console.warn('usePlayerSidebar must be used within an PlayerSidebarProvider');
      return {
        open: false,
        setOpen: () => {},
        player: null,
        setPlayer: () => {},
        playerId: null,
        setPlayerId: () => {},
      };
    }
    
  // Check if context is undefined, indicating it was used outside of a provider
  if (!context) {
      throw new Error('usePlayerSidebar must be used within an PlayerSidebarProvider');
  }
  return context;
}
