import Image from 'next/image';
import { MapTeam, MatchMode } from '../../utils/queries/types';

type GameOverviewProps = {
  time: string;
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

export default function GameOverview({
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
        <div className="text-xs capitalize">{mode}</div>
      </div>
    </section>
  );
}
