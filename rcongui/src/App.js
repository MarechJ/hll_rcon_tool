import React from 'react';
import { RouterProvider } from 'react-router-dom';
import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import durationPlugin from 'dayjs/plugin/duration';
import publicRouter from "../src/routers/public"
import adminRouter from "../src/routers/admin"
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const isPublicBuild = typeof process.env.REACT_APP_PUBLIC_BUILD === "string";

// Create a query client for React Query
const queryClient = new QueryClient();

const App = () => {
  dayjs.extend(relativeTimePlugin);
  dayjs.extend(durationPlugin);

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