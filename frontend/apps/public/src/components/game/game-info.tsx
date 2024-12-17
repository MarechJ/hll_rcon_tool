import { PublicInfo } from '../../utils/queries/types';
import MapFigure from './map-figure';
import GameOverview from './game-overview';

export default function LiveGameInfo({ game }: { game: PublicInfo }) {
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
    <article id="game-state">
      <h2 className="sr-only">Game Info</h2>
      <div className="flex flex-col-reverse xl:flex-row divide-y xl:divide-y-0">
        <GameOverview
          map={game.current_map.map}
          allies={allies}
          axis={axis}
          alliesCount={game.player_count_by_team.allied}
          axisCount={game.player_count_by_team.axis}
          mapName={mapName}
          mode={gameMode}
          score={{ axis: game.score.axis, allies: game.score.allied }}
          time={remainingTime}
        />
        <aside className="flex flex-row w-full xl:w-1/3 divide-x">
          <MapFigure
            text={'Now'}
            src={`/maps/${game.current_map.map.image_name}`}
            name={game.current_map.map.pretty_name}
            className='w-1/2 h-10 xl:h-full'
          />
          <MapFigure
            text={'Up next'}
            src={`/maps/${game.next_map.map.image_name}`}
            name={game.next_map.map.pretty_name}
            className='w-1/2 h-10 xl:h-full'
            muted
          />
        </aside>
      </div>
    </article>
  );
}
