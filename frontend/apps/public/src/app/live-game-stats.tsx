'use client';

import { liveGameStatsOptions } from '../utils/queries/live-game-stats';
import GameStats from '../components/game/game-stats';
import { liveSessionStatsOptions } from '../utils/queries/live-session-stats';
import { useSuspenseQueries } from '@tanstack/react-query';
import { PlayerWithStatus } from '../components/game/types';

export default function LiveGameStats() {
  const liveStats: { data: PlayerWithStatus[]; pending: boolean } =
    useSuspenseQueries({
      queries: [liveGameStatsOptions, liveSessionStatsOptions],
      combine: (results) => {
        const allPlayers = results[0].data.result.stats;
        const onlinePlayers = new Set(
          results[1].data.result.stats.map((player) => player.player_id)
        );
        const data = allPlayers.map((player) => ({
          ...player,
          is_online: onlinePlayers.has(player.player_id),
        }));
        return {
          data,
          pending: results.some((result) => result.isPending),
        };
      },
    });

  return <GameStats stats={liveStats.data.filter(player => player.time_seconds > 30)} />;
}
