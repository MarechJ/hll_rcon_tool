'use client';

import React, { useMemo, useState } from 'react';
import { DataTable } from './live-table';
import { columns as liveColumns } from './live-columns';
import { getSteamProfileUrl, getXboxProfileUrl, isSteamPlayer, PlayerGameDetail } from './player-game-detail';
import { Player, PlayerWithStatus } from './types';
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from '@shared/components/ui/drawer';
import { Button } from '@shared/components/ui/button';
import { isPlayerWithStatus, Status } from './player-status';
import { SimpleIcon } from '@shared/components/simple-icon';
import { siSteam } from 'simple-icons';
import Link from 'next/link';
import { Gamepad2Icon } from 'lucide-react';
import useMediaQuery from '@shared/lib/hooks/useMediaQuery'

export default function GameStats({
  stats,
}: {
  stats: Player[] | PlayerWithStatus[];
}) {
  const [selectedPlayerId, setSelectedPlayerId] = useState<
    string | undefined
  >();
  const [openDrawer, setOpenDrawer] = useState<boolean>(false);
  const isSmallScrean = useMediaQuery("screen and (max-width: 1023px)")

  const handlePlayerClick = (id: string) => {
    setSelectedPlayerId(id);
    setOpenDrawer(true);
  };

  const selectedPlayer = useMemo(
    () => stats.find((player) => player.player_id === selectedPlayerId),
    [stats, selectedPlayerId]
  );

  return (
    <section id="game-statistics">
      <h2 className="sr-only">End of game statistics</h2>
      <div className="relative flex flex-col-reverse lg:flex-row">
        <article className="w-full lg:w-2/3">
          <DataTable columns={liveColumns(handlePlayerClick)} data={stats} />
        </article>
        <aside className="hidden w-full lg:block lg:w-1/3 min-h-32">
          {selectedPlayer ? (
            <PlayerGameDetail player={selectedPlayer} />
          ) : (
            <NoPlayerGameDetail />
          )}
        </aside>
      </div>
      {isSmallScrean && selectedPlayer && (
        <MobilePlayerGameDetail
          open={openDrawer}
          setOpen={setOpenDrawer}
          player={selectedPlayer}
        />
      )}
    </section>
  );
}

function NoPlayerGameDetail() {
  return (
    <div className="w-full px-10 py-5 text-center border lg:border-l-0 lg:sticky lg:top-14">
      <div className="grid items-center border border-dashed w-full h-40 text-2xl">
        SELECT A PLAYER
      </div>
    </div>
  );
}

function MobilePlayerGameDetail({
  open,
  setOpen,
  player,
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
  player: Player;
}) {
  return (
    <Drawer open={open} onOpenChange={(open) => setOpen(open)}>
      <DrawerContent>
        <div className="mx-auto w-full max-w-sm">
          <DrawerHeader>
            <DrawerTitle>
              <div className="flex justify-center items-center gap-2 grow">
                {isPlayerWithStatus(player) && player.is_online ? (
                  <Status player={player} className="animate-ping" />
                ) : isPlayerWithStatus(player) ? (
                  <Status player={player} />
                ) : null}
                <h3 className="text-xl text-center">{player.player}</h3>
              </div>
            </DrawerTitle>
            <DrawerDescription className='sr-only'>Game statistics for {player.player}</DrawerDescription>
            <div className="flex flex-row justify-center items-center">
            <Button size={'icon'} variant={'outline'} asChild>
              {isSteamPlayer(player) ? (
                <Link
                  href={getSteamProfileUrl(player.player_id)}
                  target="_blank"
                >
                  <SimpleIcon
                    icon={siSteam}
                    size={20}
                    className="dark:fill-current"
                  />
                </Link>
              ) : (
                <Link href={getXboxProfileUrl(player.player)} target="_blank">
                  <Gamepad2Icon />
                </Link>
              )}
            </Button>
          </div>
          </DrawerHeader>
          <div className="p-4 pb-0">
            <PlayerGameDetail player={player} isMobile={true} />
          </div>
          <DrawerFooter>
            <DrawerClose asChild>
              <Button variant="outline" onClick={() => setOpen(false)}>
                Close
              </Button>
            </DrawerClose>
          </DrawerFooter>
        </div>
      </DrawerContent>
    </Drawer>
  );
}
