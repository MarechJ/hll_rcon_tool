import React from 'react'
import { createBrowserRouter, RouteObject } from 'react-router-dom'
import ErrorPage from './components/error-page'
import HomePage from './pages/home'
import Layout from './components/layout'

export const routerObjects: RouteObject[] = [
  {
    path: '/',
    element: <Layout />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
    ],
  },
]

export function createRouter(): ReturnType<typeof createBrowserRouter> {
  return createBrowserRouter(routerObjects)
}
