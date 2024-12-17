import GameOverview from '../../../components/game/game-overview';
import dayjs from 'dayjs';
import localizedFormat from 'dayjs/plugin/localizedFormat';
import MapFigure from '../../../components/game/map-figure';
import { getCompletedGameColumns } from '../../../components/game/game-columns';
import { fetchGameDetail } from '../../../utils/queries/scoreboard-maps';
import GameStats from '../../../components/game/game-stats';
import { getGameDuration } from '../utils';

dayjs.extend(localizedFormat);

type Params = {
  params: { id: string };
};

export default async function MatchDetailPage({ params }: Params) {
  const { id: matchId } = params;
  let game;

  if (!matchId || Number.isNaN(Number(matchId))) {
    return <h1>Invalid match ID</h1>;
  }

  try {
    const response = await fetchGameDetail(Number(matchId));
    game = response.result;
  } catch (e) {
    return <h1>Match with ID {matchId} not found</h1>;
  }

  const gameOverviewProps = {
    map: game.map,
    time: getGameDuration(game.start, game.end),
    axis: game.map.map.axis,
    allies: game.map.map.allies,
    mapName: game.map.pretty_name,
    mode: game.map.game_mode,
    score: {
      allies: game.result?.allied,
      axis: game.result?.axis,
    },
  };

  return (
    <>
      <div className="flex flex-col-reverse lg:flex-row divide-y lg:divide-y-0">
        <GameOverview {...gameOverviewProps} />
        <aside className="flex flex-row w-full lg:w-1/3 divide-x">
          <MapFigure
            text={dayjs(game.start).format('LLL')}
            src={`/maps/${game.map.image_name}`}
            name={game.map.map.pretty_name}
            className="w-full h-32 lg:h-full"
          />
        </aside>
      </div>
      <GameStats stats={game.player_stats} getColumns={getCompletedGameColumns} />
    </>
  );
}
