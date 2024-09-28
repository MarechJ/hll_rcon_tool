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

  const totalSeconds = dayjs(game.end).diff(dayjs(game.start), 'seconds');
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  // Format the result as hh:mm:ss
  const formattedTime = `${String(hours).padStart(2, '0')}:${String(
    minutes
  ).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  const gameOverviewProps = {
    time: formattedTime,
    axis: game.map_name.map.axis,
    allies: game.map_name.map.allies,
    mapName: game.map_name.pretty_name,
    mode: game.map_name.game_mode,
    score: {
      allies: game.result?.allied,
      axis: game.result?.axis,
    },
  };

  return (
    <>
      <GameOverview {...gameOverviewProps} />
      <GameStats stats={game.player_stats} />
    </>
  );
}
