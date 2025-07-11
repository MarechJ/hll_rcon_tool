import { Outlet } from "react-router-dom";

/**
 * Maps Manager component that serves as a container for all map-related functionality
 * This component fetches map data and passes it down to children via React Router's Outlet context
 */
function MapsManager() {
  return <Outlet />;
}

export default MapsManager;
