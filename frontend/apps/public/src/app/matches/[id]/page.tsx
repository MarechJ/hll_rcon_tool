import { fetchGameDetail } from 'apps/public/src/utils/queries/scoreboard-maps';
import GameStats from 'apps/public/src/components/game/game-stats';
import GameOverview from 'apps/public/src/components/game/game-overview';
import dayjs from 'dayjs';

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
    time: dayjs(dayjs(game.end).diff(dayjs(game.start))).format('hh:mm:ss'),
    axis: game.map.map.axis,
    allies: game.map.map.allies,
    mapName: game.map.pretty_name,
    mode: game.map.game_mode,
    score: {
      allies: game.result?.allied,
      axis: game.result?.axis
    }
  }

  return (
    <>
      <GameOverview {...gameOverviewProps} />
      <GameStats stats={game.player_stats} />
    </>
  );
}
