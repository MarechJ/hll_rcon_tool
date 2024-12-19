'use client'

import { Suspense, useEffect, useRef } from 'react'
import { validGame } from './list'
import MapFigure from '@/components/game/map-figure'
import dayjs from 'dayjs'
import localizedFormat from 'dayjs/plugin/localizedFormat'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { Link, Outlet, useLoaderData, useLocation } from 'react-router'
import { cn } from '@/lib/utils'
import { gameQueries } from '@/lib/queries/scoreboard-maps'
import { clientLoader } from './clientLoader'
import { QueryErrorResetBoundary, useSuspenseQuery } from '@tanstack/react-query'
import { ScoreboardMaps } from '@/types/api'
import { ErrorBoundary } from 'react-error-boundary'

dayjs.extend(localizedFormat)

const HorizontalGamesList = ({ games }: { games: ScoreboardMaps }) => {
  const { pathname } = useLocation()
  const gamesContainerRef = useRef<HTMLDivElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!games || !gamesContainerRef.current || !scrollAreaRef.current || !pathname) return
    const childElements = Array.from(gamesContainerRef.current?.children)
    const activeGameIndex = childElements.findIndex((el) => el.getAttribute('href') === pathname)
    const activeGameEl = childElements[activeGameIndex]
    if (activeGameEl) {
      // The static container
      const containerWidth = scrollAreaRef.current.getBoundingClientRect().width
      // The viewport of the scroll area
      const viewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      // The spacing between the items
      const spacing = 8 // space-x-2
      const itemWidth = activeGameEl.getBoundingClientRect().width + spacing
      const viewableItemsCount = containerWidth / itemWidth
      const fitsLessThanTwo = viewableItemsCount < 2
      // This is the amount of pixels to scroll by to leave the active item on the far left
      let scrollBy = containerWidth * (activeGameIndex / viewableItemsCount) - spacing
      if (fitsLessThanTwo) {
        // If the container fit less than two, display the active item in the center
        scrollBy -= containerWidth / 2 - itemWidth / 2
      } else {
        // If the container fit more than two, display the active item as the second item from the left
        scrollBy -= itemWidth
      }
      if (viewport) {
        viewport.scrollTo({ behavior: 'smooth', left: scrollBy })
      }
    }
  }, [games, gamesContainerRef, pathname, scrollAreaRef])

  return (
    <ScrollArea ref={scrollAreaRef} className='w-full whitespace-nowrap sm:-mx-4 xl:mx-0 pb-2'>
      <div ref={gamesContainerRef} className='flex flex-row w-max space-x-2'>
        {games?.maps.filter(validGame).map((game) => (
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
      <ScrollBar orientation='horizontal' />
    </ScrollArea>
  )
}

export default function GamesLayout() {
  const { page, pageSize } = useLoaderData() as Awaited<ReturnType<ReturnType<typeof clientLoader>>>
  const { data: games } = useSuspenseQuery(gameQueries.list(page, pageSize))

  return (
    <>
      <QueryErrorResetBoundary>
        {({ reset }) => (
          <ErrorBoundary
            fallbackRender={({ error, resetErrorBoundary }) => (
              <div>
                <p>An error occurred:</p>
                <pre>{error.message}</pre>
                <button onClick={resetErrorBoundary}>Try again</button>
              </div>
            )}
            onReset={reset}
          >
            <Suspense fallback={<div>Loading...</div>}>
              <HorizontalGamesList games={games} />
            </Suspense>
          </ErrorBoundary>
        )}
      </QueryErrorResetBoundary>
      <Outlet />
    </>
  )
}
