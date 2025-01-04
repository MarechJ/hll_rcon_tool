import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { RouterProvider } from 'react-router'
import { createRouter } from './router'
import { ThemeProvider } from './hooks/use-theme-provider'
import { queryClient } from './lib/queryClient'
import { LocaleHandler } from "@/i18n/locale-handler";

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system" storageKey="ui-theme">
        <LocaleHandler/>
        <RouterProvider router={createRouter()} />
      </ThemeProvider>
      <ReactQueryDevtools />
    </QueryClientProvider>
  )
}
