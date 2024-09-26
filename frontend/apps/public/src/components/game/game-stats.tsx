'use client';

import React, { useState } from 'react';
import { DataTable } from './live-table';
import { columns as liveColumns } from './live-columns';
import { PlayerGameDetail } from './player-game-detail';
import { Player } from './types';

export default function GameStats({ stats }: { stats: Player[] }) {
  const [selectedPlayer, setSelectedPlayer] = useState<Player | undefined>();

  const handlePlayerClick = (id: string) => {
    const player = stats.find((player) => player.player_id == id);
    setSelectedPlayer(player);
  };

  return (
    <section id="game-statistics">
      <h2 className="sr-only">End of game statistics</h2>
      <div className="relative flex flex-col-reverse md:flex-row">
        <article className="w-full md:w-2/3">
          <DataTable columns={liveColumns(handlePlayerClick)} data={stats} />
        </article>
        <aside className="w-full md:w-1/3 min-h-32">
          {selectedPlayer ? (
            <PlayerGameDetail player={selectedPlayer} />
          ) : (
            <NoPlayerGameDetail />
          )}
        </aside>
      </div>
    </section>
  );
}

function NoPlayerGameDetail() {
  return (
    <div className="w-full px-10 py-5 text-center border md:border-l-0 md:sticky md:top-14">
      <div className="grid items-center border border-dashed w-full h-40 text-2xl">
        SELECT A PLAYER
      </div>
    </div>
  );
}
