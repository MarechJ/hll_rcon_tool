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
  const hiddenDatesRef = useRef(hiddenDates);
  hiddenDatesRef.current = hiddenDates;
  const [hoverGameDate, setHoverGameDate] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const gameRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  const validGames = games.maps.filter(validGame);

  /**
   *  highlights the corresponding date when hovering over a game while scrolling
   *  onMouseLeave/onMouseEnter is not triggered during scrolling
   *  so we have to check manually while scrolling if mouse is within GameCard
   */
  useEffect(() => {
    const handleMouseMove = (e: any) => {
      gameRefs.current.forEach((item, key) => {
        if (hiddenDatesRef.current[validGames[key].start]) {
          return;
        }
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
  }, [hoverGameDate, validGames]);

  useEffect(() => {
    if (scrollAreaRef.current && gameRefs.current.size > 0) {
      const targetElement = Array.from(gameRefs.current.entries()).find(([index, _]) =>
        pathname.split('/')[2] === String(validGames[index].id)
      )?.[1];
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
      }
    }
  }, [pathname]);

  /**
   *  check which games are visible/hidden to determine sticky date
   */
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
      { threshold: 0, root: scrollAreaRef.current }
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
            <GameCard
              game={game}
              pathname={pathname}
              onMouseEnter={() => setHoverGameDate(game.start)}
              onMouseLeave={() => setHoverGameDate(null)}
              ref={(element: any) => {
                if (element) {
                  gameRefs.current.set(index, element);
                } else {
                  gameRefs.current.delete(index);
                }
              }}
            />
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
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
      >
        <div className="px-0.5" ref={ref} data-date={game.start}>
          <MapFigure
            text={`${dayjsLocal(game.start).format("LT")} (${dayjs(game.end).diff(dayjs(game.start), 'minutes')} ${t('time.minuteShort')})`}
            src={`/maps/${game.map.image_name}`}
            name={`${game.map.map.pretty_name} (${game.result?.allied ?? '?'}:${game.result?.axis ?? '?'})`}
            className={cn(
              "group h-20 w-64",
              pathname.split('/')[2] === String(game.id) && "border-2 border-primary"
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
