'use client';

import { usePublicInfoQuery } from '../utils/queries/public-info';
import LiveGameInfo from '../components/game/game-info';

export default function LiveGameState() {
  const [game] = usePublicInfoQuery();

  return (
    <LiveGameInfo game={game} />
  );
}
