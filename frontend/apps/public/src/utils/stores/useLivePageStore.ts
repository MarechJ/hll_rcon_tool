import { create } from 'zustand';

interface LivePageStoreState {
  playerId: string | null;
  setPlayer: (playerId: string) => void;
}

export const useLivePageStore = create<LivePageStoreState>((set) => ({
  playerId: null,
  setPlayer: (playerId) => {
    set({ playerId })
  }
}));
