import { createBrowserRouter } from "react-router-dom";
import Root from "../pages/root"

const router = createBrowserRouter([
    {
        path: '/',
        element: <Root />,
    }
]);

export default router;
