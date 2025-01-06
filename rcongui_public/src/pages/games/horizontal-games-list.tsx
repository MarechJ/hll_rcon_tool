import {ScoreboardMap, ScoreboardMaps} from "@/types/api";
import {Link, useLocation} from "react-router";
import React, {useEffect, useRef, useState} from "react";
import {ScrollArea, ScrollBar} from "@/components/ui/scroll-area";
import {validGame} from "@/pages/games/list";
import MapFigure from "@/components/game/map-figure";
import dayjs from "dayjs";
import {cn, dayjsLocal} from "@/lib/utils";
import {useTranslation} from "react-i18next";
import {useLocale} from "@/i18n/locale-provider";

export const HorizontalGamesList = ({ games }: { games: ScoreboardMaps }) => {
  const { pathname } = useLocation()
  const [hiddenDates, setHiddenDates] = useState<Record<string, boolean>>({});
  const [hoverGameDate, setHoverGameDate] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  // is used for sticky dates (position upper left corner of MapCard)
  const gameRefs = useRef<Map<string, HTMLDivElement>>(new Map());
  const gameBoundingRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  const validGames = games.maps.filter(validGame);

  /**
   *  onMouseLeave/onMouseEnter is not triggered during scrolling
   *  so we have to check manually while scrolling if mouse is within GameCard
   */
  useEffect(() => {
    const handleMouseMove = (e: any) => {
      gameBoundingRefs.current.forEach((item, key) => {
        const rect = item.getBoundingClientRect();
        if (
          e.clientX >= rect.left &&
          e.clientX <= rect.right &&
          e.clientY >= rect.top &&
          e.clientY <= rect.bottom
        ) {
          if (hoverGameDate !== validGames[key].start) {
            setHoverGameDate(validGames[key].start);
          }
        }
      });
    };

    window.addEventListener('wheel', handleMouseMove);

    return () => {
      window.removeEventListener('wheel', handleMouseMove);
    };
  }, []);

  useEffect(() => {
    if (scrollAreaRef.current && gameRefs.current.size > 0) {
      const targetElement = Array.from(gameRefs.current.entries()).find(([href, _]) =>
        pathname.startsWith(href)
      )?.[1];
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
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
  const stickyDate = visibleDates.length ? dayjsLocal(visibleDates[0][0]) : null;

  return (
    <ScrollArea ref={scrollAreaRef} className="w-full whitespace-nowrap sm:-mx-4 xl:mx-0 pb-2 relative overflow-hidden z-auto">
      <div className="flex flex-row w-max">
        {validGames.map((game, index) => (
          <React.Fragment key={game.id}>
            <div key={game.id} ref={(element: any) => {
              if (element) {
                gameBoundingRefs.current.set(index, element);
              } else {
                gameBoundingRefs.current.delete(index);
              }
            }}>
              <GameCard
                game={game}
                pathname={pathname}
                onMouseEnter={() => setHoverGameDate(game.start)}
                onMouseLeave={() => setHoverGameDate(null)}
                ref={(element) => {
                  if (element) {
                    gameRefs.current.set(`/games/${game.id}`, element);
                  } else {
                    gameRefs.current.delete(`/games/${game.id}`);
                  }
                }}
              />
            </div>
            {!dayjsLocal(game.start).isSame(dayjsLocal(validGames[index + 1]?.start), 'day') &&
              <>
                <DateCard
                  key={game.start}
                  zIndex={validGames.length - index}
                  dateString={game.start}
                  highlight={!!hoverGameDate && dayjsLocal(hoverGameDate).isSame(dayjsLocal(game.start), 'day')}
                  sticky={false}
                />
                {!!stickyDate && stickyDate.isSame(dayjsLocal(game.start), 'day') &&
                  <DateCard
                    key={`sticky-${game.start}`}
                    zIndex={validGames.length - index}
                    dateString={game.start}
                    sticky={true}
                    highlight={!!hoverGameDate && dayjsLocal(hoverGameDate).isSame(dayjsLocal(game.start), 'day')}
                  />
                }
              </>
            }
          </React.Fragment>
        ))}
      </div>
      <ScrollBar orientation="horizontal"/>
    </ScrollArea>
  );
}

const GameCard = React.forwardRef(
  (
    { game, pathname, onMouseEnter, onMouseLeave }: { game: ScoreboardMap; pathname: string; onMouseEnter: () => void, onMouseLeave: () => void },
    ref: React.Ref<HTMLDivElement>
  ) => {
    const { t } = useTranslation('translation');
    return (
      <Link
        to={`/games/${game.id}`}
        data-date={game.start}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
      >
        <div className="px-0.5">
          <div ref={ref} key={game.id} data-date={game.start}/>
          <MapFigure
            text={`${dayjsLocal(game.start).format("LT")} (${dayjs(game.end).diff(dayjs(game.start), 'minutes')} ${t('time.minuteShort')})`}
            src={`/maps/${game.map.image_name}`}
            name={`${game.map.map.pretty_name} (${game.result?.allied ?? '?'}:${game.result?.axis ?? '?'})`}
            className={cn(
              "group h-20 w-64",
              pathname.startsWith(`/games/${game.id}`) && "border-2 border-primary"
            )}
          />
        </div>
      </Link>
    );
});

const DateCard = ({ dateString, zIndex, highlight, sticky }: { dateString: string, zIndex: number, highlight: boolean, sticky: boolean }) => {
  const date = dayjsLocal(dateString);
  const globalLocaleData = useLocale().globalLocaleData;

  return (
    <div
      className={cn(
        "w-14 h-20 m-auto items-center text-center flex flex-col bg-background z-20",
        sticky && "absolute right-0 shadow-sm",
        highlight && "text-primary",
      )}
      style={{zIndex: zIndex}}
    >
      <div className="font-mono font-bold text-sm">{globalLocaleData.weekdaysShort()[date.day()].replace('.', '').toUpperCase()}</div>
      <div className="font-bold text-2xl">{date.date()}</div>
      <div className="font-mono font-bold text-lg">{globalLocaleData.monthsShort()[date.month()].replace('.', '').toUpperCase()}</div>
    </div>
  );
}
