'use client';

import { useQuery } from '@tanstack/react-query';
import React, { useEffect, useRef } from 'react';
import { gameQueries } from '../../utils/queries/scoreboard-maps';
import { validMatch } from './matches-list';
import MapFigure from '../../components/game/map-figure';
import dayjs from 'dayjs';
import localizedFormat from 'dayjs/plugin/localizedFormat';
import { ScrollArea, ScrollBar } from '@shared/components/ui/scroll-area';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@shared/utils';

dayjs.extend(localizedFormat);

export default function MatchesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { data, isLoading } = useQuery(gameQueries.list());
  const pathname = usePathname();
  const gamesContainerRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (
      isLoading ||
      !gamesContainerRef.current ||
      !scrollAreaRef.current ||
      !pathname
    )
      return;
    const childElements = Array.from(gamesContainerRef.current?.children);
    const activeGameIndex = childElements.findIndex(
      (el) => el.getAttribute('href') === pathname
    );
    const activeGameEl = childElements[activeGameIndex];
    if (activeGameEl) {
      const spacing = 8; // space-x-2
      const containerWidth = scrollAreaRef.current.getBoundingClientRect().width
      const itemWidth = activeGameEl.getBoundingClientRect().width + spacing
      const viewableItemsCount = containerWidth / itemWidth
      const fitsLessThanTwo = viewableItemsCount < 2;
      let scrollBy = containerWidth * (activeGameIndex / viewableItemsCount) - spacing
      if (fitsLessThanTwo) {
        scrollBy += itemWidth
      } else {
        scrollBy -= itemWidth
      }
      scrollAreaRef.current.scrollTo({ behavior: 'smooth', left: scrollBy });
    }
  }, [isLoading, gamesContainerRef, pathname, scrollAreaRef]);

  return (
    <>
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <ScrollArea
          ref={scrollAreaRef}
          className="w-full whitespace-nowrap -mx-4 xl:mx-0 pb-2"
        >
          <div
            ref={gamesContainerRef}
            className="flex flex-row w-max space-x-2"
          >
            {data?.result.maps.filter(validMatch).map((game) => (
              <Link key={game.id} href={`/matches/${game.id}`}>
                <MapFigure
                  text={dayjs(game.start).format('LLL')}
                  src={`/maps/${game.map.image_name}`}
                  name={`${game.map.map.pretty_name} (${
                    game.result?.allied ?? '?'
                  }:${game.result?.axis ?? '?'})`}
                  className={cn(
                    'group h-12 w-64',
                    pathname === `/matches/${game.id}` && 'border-2'
                  )}
                />
              </Link>
            ))}
          </div>
          <ScrollBar orientation="horizontal" />
        </ScrollArea>
      )}
      {children}
    </>
  );
}
