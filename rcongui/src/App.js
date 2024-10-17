import React from 'react';
import { RouterProvider } from 'react-router-dom';
import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import durationPlugin from 'dayjs/plugin/duration';
import publicRouter from "../src/routers/public"
import adminRouter from "../src/routers/admin"
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import localforage from 'localforage';
import siteConfig from './config/siteConfig';

const isPublicBuild = typeof process.env.REACT_APP_PUBLIC_BUILD === "string";

// Create a query client for React Query
const queryClient = new QueryClient();

const App = () => {
  // Dayjs plugins
  dayjs.extend(relativeTimePlugin);
  dayjs.extend(durationPlugin);

  // Configure LocalForage
  localforage.config({
    name: siteConfig.appName, // Name of the database
    storeName: isPublicBuild ? 'public' : 'admin', // Name of the data store
    version: 1.0, // Database version
    description: 'Local storage for Hell Let Loose CRCON web app', // Description for the database
    driver: [localforage.INDEXEDDB, localforage.LOCALSTORAGE], // Preferred storage drivers in order
  });

  const router = isPublicBuild ? publicRouter : adminRouter;

  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </React.StrictMode>
  );
};

export default App;
