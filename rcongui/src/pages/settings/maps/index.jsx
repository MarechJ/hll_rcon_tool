import { Outlet, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Box, Tabs, Paper } from "@mui/material";
import { get, getGameState } from "@/utils/fetchUtils.js";
import { NavLinkTab } from "@/components/shared/NavLinkTab";

/**
 * Maps Manager component that serves as a container for all map-related functionality
 * This component fetches map data and passes it down to children via React Router's Outlet context
 */
function MapsManager() {
  // Fetch maps using React Query
  const { data: maps = [] } = useQuery({
    queryKey: ["maps"],
    queryFn: async () => {
      const response = await get("get_maps");
      const data = await response.json();
      return data.result || [];
    },
  });

  // Fetch game state using React Query
  const { data: gameState } = useQuery({
    queryKey: ["gameState"],
    queryFn: async () => {
      return await getGameState();
    },
    refetchInterval: 60000, // Refetch every minute
  });

  // Get active tab
  const location = useLocation()
  const tabs = [
    { label: "List", href: "list" },
    { label: "Rotation", href: "rotation" },
    { label: "Votemap", href: "votemap" },
  ]
  const activeTab = tabs.findIndex(({ href }) => href === location.pathname.split("/").pop())

  return (
    <Box>      
      <Tabs value={activeTab} sx={{ mb: 2 }}>
        {tabs.map(({ label, href }) => (
          <NavLinkTab key={href} label={label} to={href} />
        ))}
      </Tabs>
      <Box>
        <Box sx={{ position: "relative" }}>
          {/* Pass maps and gameState data to child routes */}
          <Outlet context={{ maps, gameState }} />
        </Box>
      </Box>
    </Box>
  );
}

export default MapsManager;
