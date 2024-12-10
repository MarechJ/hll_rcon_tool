import { createBrowserRouter, RouteObject } from 'react-router-dom'
import ErrorPage from './components/error-page'
import HomePage from './pages/home'
import Layout from './components/layout'
import GamesLayout from './pages/games/layout'
import GamesList from './pages/games'
import GameDetail from './pages/games/[id]'
import { queryClient } from './lib/queryClient'
import { clientLoader as layoutClientLoader } from './components/layout/clientLoader'
import { clientLoader as homeClientLoader } from './pages/home/clientLoader'
import { clientLoader as gameClientLoader } from './pages/games/clientLoader'
import { clientLoader as gameDetailClientLoader } from './pages/games/[id]/clientLoader'

export const routerObjects: RouteObject[] = [
  {
    path: '/',
    element: <Layout />,
    errorElement: <ErrorPage />,
    loader: layoutClientLoader(queryClient),
    children: [
      {
        index: true,
        errorElement: <ErrorPage />,
        element: <HomePage />,
        loader: homeClientLoader(queryClient),
      },
      {
        path: '/games',
        element: <GamesLayout />,
        errorElement: <ErrorPage />,
        loader: gameClientLoader(queryClient),
        children: [
          {
            index: true,
            element: <GamesList />,
            loader: gameClientLoader(queryClient),
          },
          {
            path: ':id',
            element: <GameDetail />,
            loader: gameDetailClientLoader(queryClient),
          },
        ],
      },
    ],
  },
]

export function createRouter(): ReturnType<typeof createBrowserRouter> {
  return createBrowserRouter(routerObjects)
}
