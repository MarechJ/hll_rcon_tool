import {ScoreboardMap, ScoreboardMaps} from "@/types/api";
import {Link, useLocation} from "react-router";
import React, {useEffect, useRef, useState} from "react";
import {ScrollArea, ScrollBar} from "@/components/ui/scroll-area";
import {validGame} from "@/pages/games/list";
import MapFigure from "@/components/game/map-figure";
import dayjs, {Dayjs} from "dayjs";
import {cn, dayjsLocal} from "@/lib/utils";
import {useTranslation} from "react-i18next";
import {useLocale} from "@/i18n/locale-provider";

export const HorizontalGamesList = ({ games }: { games: ScoreboardMaps }) => {
  const { pathname } = useLocation()
  const [gamesVisibility, setGamesVisibility] = useState<Record<number, boolean>>({});
  const gamesVisibilityRef = useRef(gamesVisibility);
  gamesVisibilityRef.current = gamesVisibility;
  const [hoverGameDate, setHoverGameDate] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const gameRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  const validGames = games.maps.filter(validGame);
  const cardsData = validGames.flatMap((game, index) => dayjsLocal(game.start).isSame(dayjsLocal(validGames[index + 1]?.start), 'day') ? [game] : [game, game.start]);

  /**
   *  highlights the corresponding date when hovering over a game while scrolling
   *  onMouseLeave/onMouseEnter is not triggered during scrolling
   *  so we have to check manually while scrolling if mouse is within GameCard
   */
  useEffect(() => {
    const handleMouseMove = (e: any) => {
      gameRefs.current.forEach((item, gameId) => {
        if (!gamesVisibilityRef.current[gameId]) {
          return;
        }
        const rect = item.getBoundingClientRect();
        if (
          e.clientX >= rect.left &&
          e.clientX <= rect.right &&
          e.clientY >= rect.top &&
          e.clientY <= rect.bottom
        ) {
          const game = validGames.find(game => game.id === gameId);
          if (game && hoverGameDate !== game.start) {
            setHoverGameDate(game.start);
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
      const targetElement = Array.from(gameRefs.current.entries()).find(([gameId, _]) =>
        pathname.split('/')[2] === String(gameId)
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
          const gameId = entry.target.getAttribute('data-id');
          if (gameId) {
            setGamesVisibility(prev => ({
              ...prev,
              [Number(gameId)]: entry.isIntersecting
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


  const visibleGames = Object.entries(gamesVisibility).filter(([_, visible]) => visible);
  const stickyDateString = !!visibleGames.length && validGames.find(game => game.id === Number(visibleGames[0][0]))?.start;

  return (
    <ScrollArea ref={scrollAreaRef} className="w-full whitespace-nowrap sm:-mx-4 xl:mx-0 pb-2 relative overflow-hidden z-0">
      <div className="flex flex-row w-max">
        {cardsData.map((cardData, index) => {
          return typeof cardData !== 'string' ?
            <div
              ref={(element: any) => {
                if (element) {
                  gameRefs.current.set(cardData.id, element);
                } else {
                  gameRefs.current.delete(cardData.id);
                }
              }}
              data-id={cardData.id}
            >
              <GameCard
                game={cardData}
                pathname={pathname}
                onMouseEnter={React.useCallback(() => setHoverGameDate(cardData.start), [cardData])}
                onMouseLeave={React.useCallback(() => setHoverGameDate(null), [])}
              />
            </div>
            :
            <DateCard
              key={cardData}
              zIndex={cardsData.length - index}
              date={dayjsLocal(cardData)}
              highlight={!!hoverGameDate && dayjsLocal(hoverGameDate).isSame(dayjsLocal(cardData), 'day')}
              sticky={false}
            />
        })}
        {stickyDateString &&
          <DateCard
            key={`sticky-${stickyDateString}`}
            zIndex={cardsData.length - cardsData.findIndex(card => typeof card === 'string' && dayjsLocal(card).isSame(dayjsLocal(stickyDateString), 'day'))}
            date={dayjsLocal(stickyDateString)}
            sticky={true}
            highlight={!!hoverGameDate && dayjsLocal(hoverGameDate).isSame(dayjsLocal(stickyDateString), 'day')}
          />
        }
      </div>
      <ScrollBar orientation="horizontal"/>
    </ScrollArea>
  );
}

const GameCard = React.memo(
  (
    { game, pathname, onMouseEnter, onMouseLeave }: { game: ScoreboardMap; pathname: string; onMouseEnter: () => void, onMouseLeave: () => void }
  ) => {
    const { t } = useTranslation('translation');
    return (
      <Link
        to={`/games/${game.id}`}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
      >
        <div className="px-0.5">
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

const DateCard = ({ date, zIndex, highlight, sticky }: { date: Dayjs, zIndex: number, highlight: boolean, sticky: boolean }) => {
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
