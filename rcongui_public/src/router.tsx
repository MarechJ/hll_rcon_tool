import React from 'react'
import { createBrowserRouter, RouteObject } from 'react-router-dom'
import ErrorPage from './components/error-page'
import HomePage from './pages/home'
import Layout from './components/layout'
import GamesLayout from './pages/games/layout'
import GamesList from './pages/games'
import GameDetail from './pages/games/[id]'

export const routerObjects: RouteObject[] = [
  {
    path: '/',
    element: <Layout />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        errorElement: <ErrorPage />,
        element: <HomePage />,
      },
      {
        path: '/games',
        element: <GamesLayout />,
        errorElement: <ErrorPage />,
        children: [
          {
            index: true,
            element: <GamesList />,
          },
          {
            path: ':id',
            element: <GameDetail />,
          },
        ],
      },
    ],
  },
]

export function createRouter(): ReturnType<typeof createBrowserRouter> {
  return createBrowserRouter(routerObjects)
}
