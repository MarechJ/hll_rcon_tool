import React from 'react';
import { RouterProvider } from 'react-router-dom';
import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import durationPlugin from 'dayjs/plugin/duration';
import adminRouter from "./router"
import publicRouter from "./public-router"
import { QueryClientProvider } from '@tanstack/react-query';
import localforage from 'localforage';
import siteConfig from './config/siteConfig';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from './queryClient';

const router = process.env.REACT_APP_PUBLIC_BUILD ? publicRouter : adminRouter;

const App = () => {
  // Dayjs plugins
  dayjs.extend(relativeTimePlugin);
  dayjs.extend(durationPlugin);

  // Configure LocalForage
  localforage.config({
    name: siteConfig.appName, // Name of the database
    storeName: 'admin', // Name of the data store
    version: 1.0, // Database version
    description: 'Local storage for Hell Let Loose CRCON web app', // Description for the database
    driver: [localforage.INDEXEDDB, localforage.LOCALSTORAGE], // Preferred storage drivers in order
  });

  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </React.StrictMode>
  );
};

export default App;