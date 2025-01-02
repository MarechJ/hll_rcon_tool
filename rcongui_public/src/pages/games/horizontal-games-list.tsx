import {ScoreboardMap, ScoreboardMaps} from "@/types/api";
import {Link, useLocation} from "react-router";
import {useRef} from "react";
import {ScrollArea, ScrollBar} from "@/components/ui/scroll-area";
import {validGame} from "@/pages/games/list";
import MapFigure from "@/components/game/map-figure";
import dayjs from "dayjs";
import {cn} from "@/lib/utils";
import localizedFormat from "dayjs/plugin/localizedFormat";
import {Calendar} from "lucide-react";
import {useTranslation} from "react-i18next";

dayjs.extend(localizedFormat)

export const HorizontalGamesList = ({ games }: { games: ScoreboardMaps }) => {
  const { pathname } = useLocation()

  const scrollAreaRef = useRef<HTMLDivElement>(null)

  const validGames = games.maps.filter(validGame);

  return (
    <ScrollArea ref={scrollAreaRef} className="w-full whitespace-nowrap sm:-mx-4 xl:mx-0 pb-2">
      <div className="flex flex-row w-max space-x-2">
        {validGames.map((game, index) => (
          <>
            <GameCard game={game} pathname={pathname}/>
            {!dayjs(game.start).isSame(dayjs(validGames[index + 1]?.start), 'day') &&
              <DateCard dateString={game.start}/>
            }
          </>
        ))}
      </div>
      <ScrollBar orientation="horizontal" />
    </ScrollArea>
  )
}

const GameCard = ({ game, pathname }: { game: ScoreboardMap, pathname: string }) => {
  return <Link key={game.id} to={`/games/${game.id}`}>
    <MapFigure
      text={dayjs(game.start).format('LLL')}
      src={`/maps/${game.map.image_name}`}
      name={`${game.map.map.pretty_name} (${game.result?.allied ?? '?'}:${game.result?.axis ?? '?'})`}
      className={cn('group h-20 w-64', pathname.startsWith(`/games/${game.id}`) && 'border-2 border-primary')}
    />
  </Link>
}

const DateCard = ({ dateString }: { dateString: string }) => {
  const { t } = useTranslation('translation');

  const date = dayjs(dateString);
  return <div className="w-10 h-full m-auto items-center text-center flex flex-col">
    <Calendar/>
    <div>{date.date()}</div>
    <div>{(t(`month.${date.month()}` as unknown as TemplateStringsArray) as string).toUpperCase()}</div>
  </div>
}
