import Image from 'next/image';
import { MapTeam, MatchMap, MatchMode } from '../../utils/queries/types';
import React from 'react';
import { cn } from '@shared/utils';
import { LockIcon } from 'lucide-react';

type GameOverviewProps = {
  time: string;
  map: MatchMap;
  allies: MapTeam;
  axis: MapTeam;
  mode: MatchMode;
  mapName: string;
  alliesCount?: number;
  axisCount?: number;
  score: {
    allies: number | undefined;
    axis: number | undefined;
  };
};

const romanDigits = ['I', 'II', 'III', 'IV', 'V'];

function RectangleNeutral() {
  return (
    <div
      className={cn(
        'text-center basis-1/5 w-1/5 bg-neutral-200 [clip-path:polygon(0%_0%,100%_0,95%_50%,100%_100%,0%_100%,5%_50%)]'
      )}
    ></div>
  );
}

function Arrow({
  team,
  highlighted,
  mode,
  order,
  direction,
}: {
  team?: 'axis' | 'allies';
  mode?: 'warfare' | 'offensive' | 'skirmish';
  highlighted?: boolean;
  order?: number;
  direction: 'left' | 'right';
}) {
  return (
    <div
      className={cn(
        'grid items-center justify-center text-center basis-1/5 w-1/5 border-t-4',
        direction === 'right' &&
          '[clip-path:polygon(0%_0%,95%_0%,100%_50%,95%_100%,0%_100%,5%_50%)]',
        direction === 'left' &&
          '[clip-path:polygon(5%_0%,100%_0,95%_50%,100%_100%,5%_100%,0%_50%)]',
        team === 'axis' && 'bg-red-300 border-red-500',
        team === 'allies' && 'bg-blue-300 border-blue-500',
        highlighted && 'opacity-100 border-t-0',
        highlighted && team === 'axis' && 'bg-red-500',
        highlighted && team === 'allies' && 'bg-blue-500'
      )}
    >
      {!highlighted && mode === 'warfare' && (
        <LockIcon className="stroke-[3] size-2 md:stroke-[4] md:size-3 lg:size-4 lg:stroke-[5]" />
      )}
      {mode === 'offensive' && order !== undefined && (
        <span>{romanDigits[order]}</span>
      )}
    </div>
  );
}

export default function GameOverview({
  map,
  time,
  allies,
  axis,
  mode,
  mapName,
  axisCount,
  alliesCount,
  score,
}: GameOverviewProps) {
  return (
    <section className="flex flex-col w-full lg:w-2/3 pt-1">
      <div className="w-full h-4 md:h-6 lg:h-8 flex flex-row px-2 mb-1">
        {map.game_mode === 'warfare' ? (
          <>
            {Array(score.allies)
              .fill(null)
              .map((_, index, arr) => (
                <Arrow
                  key={`score-${index}`}
                  direction="right"
                  team="allies"
                  mode="warfare"
                  highlighted={
                    index === arr.length - 1 &&
                    score.allies !== score.axis &&
                    score.allies !== 5 &&
                    score.axis !== 5
                  }
                />
              ))}
            {score.allies === score.axis && <RectangleNeutral />}
            {Array(score.axis)
              .fill(null)
              .map((_, index, arr) => (
                <Arrow
                  key={`score-${index}`}
                  direction="left"
                  team="axis"
                  mode="warfare"
                  highlighted={
                    index === 0 &&
                    score.allies !== score.axis &&
                    score.allies !== 5 &&
                    score.axis !== 5
                  }
                />
              ))}
          </>
        ) : map.game_mode === 'offensive' ? (
          <>
            {Array(score.allies)
              .fill(null)
              .map((_, index, arr) => {
                return (
                  <Arrow
                    key={`score-${index}`}
                    direction={map.attackers === 'allies' ? 'right' : 'left'}
                    team="allies"
                    mode={'offensive'}
                    order={index}
                    highlighted={index === 4}
                  />
                );
              })}
            {Array(score.axis)
              .fill(null)
              .map((_, index) => {
                return (
                  <Arrow
                    key={`score-${index}`}
                    direction={map.attackers === 'allies' ? 'right' : 'left'}
                    team="axis"
                    mode={'offensive'}
                    highlighted={index === 0}
                    order={(score.allies ?? 0) + index}
                  />
                );
              })}
          </>
        ) : null}
      </div>
      <div className="text-sm text-center">{time}</div>
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
              {alliesCount !== undefined && (
                <div className="flex-grow sm:flex-grow-0">
                  {alliesCount} Player
                  {alliesCount !== 1 && 's'}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="text-4xl lg:text-6xl basis-1/2 min-w-24 lg:min-w-40 text-center">
          {score.allies ?? '?'} : {score.axis ?? '?'}
        </div>

        <div className="flex flex-row justify-between basis-full">
          <div className="flex flex-col text-left w-full">
            <div className="text-lg lg:text-2xl font-bold uppercase">
              {axis.team}
            </div>
            <div className="flex flex-row text-sm">
              {axisCount !== undefined && (
                <div>
                  {axisCount} Player
                  {axisCount !== 1 && 's'}
                </div>
              )}
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
        <div className="text-xs capitalize">
          {mode}
          {map.attackers && ` - ${map.attackers}`}
        </div>
      </div>
    </section>
  );
}
