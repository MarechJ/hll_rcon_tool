import {ScoreboardMap, ScoreboardMaps} from "@/types/api";
import {Link, useLocation} from "react-router";
import React, {useEffect, useRef, useState} from "react";
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
  const [hiddenDates, setHiddenDates] = useState<Record<string, boolean>>({});
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const gameRefs = useRef<Map<string, HTMLDivElement>>(new Map());

  const validGames = games.maps.filter(validGame);

  useEffect(() => {
    if (scrollAreaRef.current && gameRefs.current.size > 0) {
      const targetElement = Array.from(gameRefs.current.entries()).find(([href, _]) =>
        pathname.startsWith(href)
      )?.[1];
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: "smooth", inline: "center" });
      }
    }
  }, [pathname]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          const dateId = entry.target.getAttribute('data-date');
          if (dateId) {
            setHiddenDates(prev => ({
              ...prev,
              [dateId]: !entry.isIntersecting
            }));
          }
        });
      },
      { threshold: 1, root: scrollAreaRef.current }
    );

    gameRefs.current.values().forEach((ref) => {
      if (ref) observer.observe(ref);
    });

    return () => observer.disconnect();
  }, []);

  const visibleDates = Object.entries(hiddenDates).filter(([key, value], index) => !value && (index + 1 === Object.entries(hiddenDates).length || Object.values(hiddenDates)[index + 1]));
  const stickyDate = visibleDates.length ? dayjs(visibleDates[0][0]) : null;

  return (
    <ScrollArea ref={scrollAreaRef} className="w-full whitespace-nowrap sm:-mx-4 xl:mx-0 pb-2">
      <div className="flex flex-row w-max space-x-2">
        {validGames.map((game, index) => (
          <>
            <GameCard
              key={game.id}
              game={game}
              pathname={pathname}
              ref={(element) => {
                if (element) {
                  gameRefs.current.set(`/games/${game.id}`, element);
                } else {
                  gameRefs.current.delete(`/games/${game.id}`);
                }
              }}
            />
            {!dayjs(game.start).isSame(dayjs(validGames[index + 1]?.start), 'day') &&
              <DateCard
                key={game.start}
                dateString={game.start}
                isSticky={dayjs(stickyDate).isSame(dayjs(game.start), 'day')}
              />
            }
          </>
        ))}
      </div>
      <ScrollBar orientation="horizontal"/>
    </ScrollArea>
  );
}

const GameCard = React.forwardRef(
  (
    { game, pathname }: { game: ScoreboardMap; pathname: string },
    ref: React.Ref<HTMLDivElement>
  ) => {
    return (
      <Link to={`/games/${game.id}`} data-date={game.start}>
        <div ref={ref} key={game.id} data-date={game.start} className={"left-5 relative"}/>
        <MapFigure
          text={dayjs(game.start).format("LLL")}
          src={`/maps/${game.map.image_name}`}
          name={`${game.map.map.pretty_name} (${game.result?.allied ?? '?'}:${game.result?.axis ?? '?'})`}
          className={cn(
            "group h-20 w-64",
            pathname.startsWith(`/games/${game.id}`) && "border-2 border-primary"
          )}
        />
      </Link>
    );
  }
);

const DateCard = ({ dateString, isSticky }: { dateString: string, isSticky: boolean }) => {
  const { t } = useTranslation('translation');
  const date = dayjs(dateString);

  return (
    <div className={cn(
      "w-10 h-20 m-auto items-center text-center flex flex-col",
      isSticky && "sticky right-0 shadow-sm bg-background"
    )}>
      <Calendar />
      <div>{date.date()}</div>
      <div>{(t(`month.${date.month()}` as unknown as TemplateStringsArray) as string).toUpperCase()}</div>
    </div>
  );
}
