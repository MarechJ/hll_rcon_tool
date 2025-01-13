import { PublicInfo } from '@/types/api'
import GameOverview from '@/components/game/overview'
import MapFigure from '@/components/game/map-figure'
import { useTranslation } from 'react-i18next'
import React from "react";
import {Link} from "react-router";
import {ToggleGroup, ToggleGroupItem} from "@/components/ui/toggle-group";
import {TableIcon} from "lucide-react";
import {siTwitch} from "simple-icons";
import {SimpleIcon} from "@/components/simple-icon";

export default function LiveGameInfo({ game }: { game: PublicInfo }) {
  const { t } = useTranslation('translation')

  const remainingTime = `${String(Math.floor(game.time_remaining / 3600))}:${String(
    Math.floor((game.time_remaining % 3600) / 60),
  ).padStart(2, '0')}:${String(game.time_remaining % 60).padStart(2, '0')}`
  const allies = game.current_map.map.map.allies
  const axis = game.current_map.map.map.axis
  const gameMode = game.current_map.map.game_mode
  const mapName = game.current_map.map.map.pretty_name

  return (
    <>
      <article id="game-state">
        <h2 className="sr-only">Game Info</h2>
        <div className="flex flex-col-reverse lg:flex-row divide-y lg:divide-y-0">
          <section className="w-full lg:w-2/3">
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
            <ToggleGroup type="single" variant="outline" className="p-4">
              <ToggleGroupItem value={`/`} asChild>
                <Link to={`/`}>
                  <TableIcon size={20}/>
                </Link>
              </ToggleGroupItem>
              <ToggleGroupItem value={`/streaming`} asChild>
                <Link to={`/streaming`}>
                  <SimpleIcon icon={siTwitch} size={20} className="dark:fill-current" />
                </Link>
              </ToggleGroupItem>
            </ToggleGroup>
          </section>
          <aside className="flex flex-row w-full lg:w-1/3 divide-x">
            <MapFigure
              text={t('now')}
              src={`/maps/${game.current_map.map.image_name}`}
              name={game.current_map.map.pretty_name}
              className="w-1/2 max-h-16 lg:max-h-full"
            />
            <MapFigure
              text={t('up-next')}
              src={`/maps/${game.next_map.map.image_name}`}
              name={game.next_map.map.pretty_name}
              className="w-1/2 max-h-16 lg:max-h-full"
              muted
            />
          </aside>
        </div>
      </article>
    </>
  )
}
