import { createBrowserRouter } from "react-router-dom";
import PublicRoot from "@/public-pages/root";
import LiveGamePage from "./public-pages";
import { loader as liveGamePageLoader } from "./public-pages";
import GamesPage, { loader as gamesPageLoader } from "./public-pages/games";
import CompletedGamePage, {
  loader as completedGamePageLoader,
} from "./public-pages/games/[gameId]";

const router = createBrowserRouter([
  {
    path: "/",
    element: <PublicRoot />,
    children: [
      {
        path: "/",
        index: true,
        element: <LiveGamePage />,
        loader: liveGamePageLoader,
      },
      {
        path: "/games",
        element: <GamesPage />,
        loader: gamesPageLoader,
      },
      {
        path: "/games/:gameId",
        element: <CompletedGamePage />,
        loader: completedGamePageLoader,
      },
    ],
  },
]);

export default router;
