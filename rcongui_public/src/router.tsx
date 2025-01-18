import { createBrowserRouter, RouteObject } from 'react-router'
import ErrorPage from './components/error-page'
import GameLiveLayout from './pages/home/layout'
import Layout from './components/layout'
import GamesLayout from './pages/games/layout'
import GamesList from './pages/games'
import GameDetail from './pages/games/[id]'
import GameDetailLayout from './pages/games/[id]/layout'
import GameDetailCharts from './pages/games/[id]/charts'
import { queryClient } from './lib/queryClient'
import { clientLoader as layoutClientLoader } from './components/layout/clientLoader'
import { clientLoader as homeClientLoader } from './pages/home/clientLoader'
import { clientLoader as gameClientLoader } from './pages/games/clientLoader'
import { clientLoader as gameDetailClientLoader } from './pages/games/[id]/clientLoader'
import GameDetailLive from "@/pages/home";
import React from "react";
import Streaming from "@/pages/home/streaming";

export const routerObjects: RouteObject[] = [
  {
    path: '/',
    element: <Layout />,
    errorElement: <ErrorPage />,
    loader: layoutClientLoader(queryClient),
    children: [
      {
        path: '/',
        errorElement: <ErrorPage />,
        element: <GameLiveLayout />,
        loader: homeClientLoader(queryClient),
        children: [
          {
            index: true,
            element: <GameDetailLive />,
          },
          {
            path: '/streaming',
            element: <Streaming />,
          },
        ]
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
            path: ':id/*',
            element: <GameDetailLayout />,
            loader: gameDetailClientLoader(queryClient),
            children: [
              {
                index: true,
                element: <GameDetail />,
              },
              {
                path: 'charts',
                element: <GameDetailCharts />,
              },
            ],
          },
        ],
      },
    ],
  },
]

export function createRouter(): ReturnType<typeof createBrowserRouter> {
  return createBrowserRouter(routerObjects)
}
