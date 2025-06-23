import { Outlet, useLocation } from "react-router-dom";
import { Box, Tabs } from "@mui/material";
import { NavLinkTab } from "@/components/shared/NavLinkTab";

/**
 * Maps Manager component that serves as a container for all map-related functionality
 * This component fetches map data and passes it down to children via React Router's Outlet context
 */
function MapsManager() {
  // Get active tab
  const location = useLocation()
  const tabs = [
    { label: "List", href: "/settings/maps/list" },
    { label: "Rotation", href: "/settings/maps/rotation" },
    { label: "Votemap", href: "/settings/maps/votemap" },
    { label: "Objectives", href: "/settings/maps/objectives" },
  ]
  const activeTab = tabs.findIndex(({ href }) => location.pathname.startsWith(href))

  return (
    <Box>      
      <Tabs value={activeTab}>
        {tabs.map(({ label, href }) => (
          <NavLinkTab key={href} label={label} to={href} />
        ))}
      </Tabs>
      <Box>
        <Outlet />
      </Box>
    </Box>
  );
}

export default MapsManager;
