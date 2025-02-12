import { RouterProvider } from 'react-router-dom';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import durationPlugin from 'dayjs/plugin/duration';
import adminRouter from "./router"
import { QueryClientProvider } from '@tanstack/react-query';
import localforage from 'localforage';
import siteConfig from './config/siteConfig';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from './queryClient';
import {StrictMode} from "react";
import AppTheme from "@/themes/AppTheme";
import { CssBaseline } from '@mui/material';
import { useAppStore } from './stores/app-state';

const App = () => {
  // Dayjs plugins
  dayjs.extend(relativeTimePlugin);
  dayjs.extend(durationPlugin);
  dayjs.extend(utc);

  // Configure LocalForage
  localforage.config({
    name: siteConfig.appName, // Name of the database
    storeName: 'admin', // Name of the data store
    version: 1.0, // Database version
    description: 'Local storage for Hell Let Loose CRCON web app', // Description for the database
    driver: [localforage.INDEXEDDB, localforage.LOCALSTORAGE], // Preferred storage drivers in order
  });

  const colorScheme = useAppStore((state) => state.colorScheme);

  return (
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <AppTheme selectedScheme={colorScheme}>
          <CssBaseline enableColorScheme />
          <RouterProvider router={adminRouter} />
          <ReactQueryDevtools initialIsOpen={false} />
        </AppTheme>
      </QueryClientProvider>
    </StrictMode>
  );
};

export default App;
