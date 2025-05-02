import { Outlet } from "react-router-dom";
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

  return (
    <Box>      
      {/* Pass maps and gameState data to child routes */}
      <Tabs>
        <NavLinkTab label="List" to="list" />
        <NavLinkTab label="Rotation" to="rotation" />
        <NavLinkTab label="Votemap" to="votemap" />
      </Tabs>
      <Box sx={{ mt: 2 }}>
        <Paper sx={{ p: 3, position: "relative" }}>
          <Outlet context={{ maps, gameState }} />
        </Paper>
      </Box>
    </Box>
  );
}

export default MapsManager;
