'use client';

import Image from 'next/image';
import { usePublicInfoQuery } from '../utils/queries/public-info';

export default function GameState() {
  const [game] = usePublicInfoQuery();

  const remainingTime = `${String(
    Math.floor(game.time_remaining / 3600)
  )}:${String(Math.floor((game.time_remaining % 3600) / 60)).padStart(
    2,
    '0'
  )}:${String(game.time_remaining % 60).padStart(2, '0')}`;
  const allies = game.current_map.map.map.allies;
  const axis = game.current_map.map.map.axis;
  const gameMode = game.current_map.map.game_mode;
  const mapName = game.current_map.map.map.pretty_name;

  return (
    <section id="game-state">
      <h2 className="sr-only">Game Info</h2>
      <div className="flex flex-col-reverse xl:flex-row divide-y-2">
        <article className="flex flex-col w-full xl:w-2/3 pt-1">
          <div className="text-sm text-center">{remainingTime}</div>
          <div className="flex flex-row justify-center items-center lg:px-2">
            <div className="flex flex-row justify-between basis-full">
              <div className="flex justify-start size-12 lg:size-16">
                <Image
                  src={`/teams/${allies.name}.webp`}
                  alt={allies.team}
                  width={64}
                  height={64}
                />
              </div>
              <div className="flex flex-col text-right flex-grow">
                <div className="text-lg lg:text-2xl font-bold uppercase">
                  {allies.team}
                </div>
                <div className="flex flex-row text-sm">
                  <div className="hidden sm:block flex-grow self-center border-b-[6px] mx-1 border-blue-500 border-double"></div>
                  <div className="flex-grow sm:flex-grow-0">
                    {game.player_count_by_team.allied} Player
                    {game.player_count_by_team.allied !== 1 && 's'}
                  </div>
                </div>
              </div>
            </div>

            <div className="text-4xl lg:text-6xl basis-1/2 min-w-24 lg:min-w-40 text-center">
              {game.score.allied} : {game.score.axis}
            </div>

            <div className="flex flex-row justify-between basis-full">
              <div className="flex flex-col text-left w-full">
                <div className="text-lg lg:text-2xl font-bold uppercase">
                  {axis.team}
                </div>
                <div className="flex flex-row text-sm">
                  <div>
                    {game.player_count_by_team.axis} Player
                    {game.player_count_by_team.axis !== 1 && 's'}
                  </div>
                  <div className="hidden sm:block flex-grow self-center border-b-[6px] mx-1 border-red-500 border-double"></div>
                </div>
              </div>
              <div className="flex justify-start size-12 lg:size-16">
                <Image
                  src={`/teams/${axis.name}.webp`}
                  alt={axis.team}
                  width={64}
                  height={64}
                  style={{ maxWidth: 'none' }}
                />
              </div>
            </div>
          </div>
          <div className="flex flex-col text-center justify-between">
            <div className="flex flex-row">
              <div className="sm:hidden w-full self-center border-t-[6px] mx-1 border-blue-500 border-double"></div>
              <div className="sm:w-full min-w-fit text-sm">{mapName}</div>
              <div className="sm:hidden w-full self-center border-t-[6px] mx-1 border-red-500 border-double"></div>
            </div>
            <div className="text-xs capitalize">{gameMode}</div>
          </div>
        </article>
        <aside className="flex flex-row w-full xl:w-1/3 divide-x-2">
          <figure className="relative w-1/2 h-10 xl:h-full">
            <Image
              src={`/maps/${game.current_map.map.image_name}`}
              alt=""
              fill
              style={{ objectFit: 'cover' }}
              className="saturate-200"
            />
            <figcaption className="absolute bottom-0 w-full p-1 text-center text-sm font-bold bg-background/75">
              <div className="text-xs">Now</div>
              <div>{game.current_map.map.pretty_name}</div>
            </figcaption>
          </figure>
          <figure className="relative w-1/2 h-10 xl:h-full">
            <Image
              src={`/maps/${game.next_map.map.image_name}`}
              alt=""
              fill
              style={{ objectFit: 'cover' }}
              className="grayscale-[50]"
            />
            <figcaption className="absolute bottom-0 w-full p-1 text-center text-sm font-bold bg-background/75">
              <div className="text-xs">Up next</div>
              <div>{game.next_map.map.pretty_name}</div>
            </figcaption>
          </figure>
        </aside>
      </div>
    </section>
  );
}
