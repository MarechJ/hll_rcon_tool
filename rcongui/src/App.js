import React from 'react';
import { RouterProvider } from 'react-router-dom';
import dayjs from 'dayjs';
import relativeTimePlugin from 'dayjs/plugin/relativeTime';
import publicRouter from "../src/routers/public"
import adminRouter from "../src/routers/admin"

const isPublicBuild = typeof process.env.REACT_APP_PUBLIC_BUILD === "string";

const App = () => {
  dayjs.extend(relativeTimePlugin);

  const router = isPublicBuild ? publicRouter : adminRouter;

  return (
    <React.StrictMode>
      <RouterProvider router={router} />
    </React.StrictMode>
  );
};

export default App;