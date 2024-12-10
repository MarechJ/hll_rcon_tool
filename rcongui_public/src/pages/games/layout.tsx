'use client'

import { Suspense, useEffect, useRef } from 'react'
import { validMatch } from './list'
import MapFigure from '@/components/game/map-figure'
import dayjs from 'dayjs'
import localizedFormat from 'dayjs/plugin/localizedFormat'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useGames } from '@/lib/queries/scoreboard-maps'

dayjs.extend(localizedFormat)

export default function GamesLayout() {
  const [games, { isLoading }] = useGames()
  const { pathname } = useLocation()
  const gamesContainerRef = useRef<HTMLDivElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!games ||isLoading || !gamesContainerRef.current || !scrollAreaRef.current || !pathname) return
    const childElements = Array.from(gamesContainerRef.current?.children)
    const activeGameIndex = childElements.findIndex((el) => el.getAttribute('href') === pathname)
    const activeGameEl = childElements[activeGameIndex]
    if (activeGameEl) {
      const spacing = 8 // space-x-2
      const containerWidth = scrollAreaRef.current.getBoundingClientRect().width
      const itemWidth = activeGameEl.getBoundingClientRect().width + spacing
      const viewableItemsCount = containerWidth / itemWidth
      // const fitsLessThanTwo = viewableItemsCount < 2;
      const scrollBy = containerWidth * (activeGameIndex / viewableItemsCount) - spacing
      // if (fitsLessThanTwo) {
      //   scrollBy += itemWidth
      // } else {
      //   scrollBy -= itemWidth
      // }
      const viewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (viewport) {
        viewport.scrollTo({ behavior: 'smooth', left: scrollBy })
      }
    }
  }, [games,isLoading, gamesContainerRef, pathname, scrollAreaRef])

  return (
    <>
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <Suspense fallback={<div>SUSPENDED...</div>}>
          <ScrollArea ref={scrollAreaRef} className="w-full whitespace-nowrap -mx-4 xl:mx-0 pb-2">
            <div ref={gamesContainerRef} className="flex flex-row w-max space-x-2">
              {games?.maps.filter(validMatch).map((game) => (
                <Link key={game.id} to={`/games/${game.id}`}>
                  <MapFigure
                    text={dayjs(game.start).format('LLL')}
                    src={`/maps/${game.map.image_name}`}
                    name={`${game.map.map.pretty_name} (${game.result?.allied ?? '?'}:${game.result?.axis ?? '?'})`}
                    className={cn('group h-12 w-64', pathname === `/games/${game.id}` && 'border-2 border-primary')}
                  />
                </Link>
              ))}
            </div>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>
        </Suspense>
      )}
      <Outlet />
    </>
  )
}
