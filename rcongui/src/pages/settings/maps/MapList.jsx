import { Box, Typography } from "@mui/material";
import { MapListItem } from "./rotation/MapListItem";

const EmptyMapList = () => {
  return (
    <Box
      sx={{
        py: 5,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        color: "text.secondary",
      }}
    >
      <Box sx={{ mb: 2, opacity: 0.5 }}>
        <svg width="48" height="48" viewBox="0 0 24 24">
          <path
            fill="currentColor"
            d="M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,12.5A1.5,1.5 0 0,1 10.5,11A1.5,1.5 0 0,1 12,9.5A1.5,1.5 0 0,1 13.5,11A1.5,1.5 0 0,1 12,12.5M12,7.2C9.9,7.2 8.2,8.9 8.2,11C8.2,14 12,17.5 12,17.5C12,17.5 15.8,14 15.8,11C15.8,8.9 14.1,7.2 12,7.2Z"
          />
        </svg>
      </Box>
      <Typography variant="h6" gutterBottom>
        No maps found
      </Typography>
      <Typography variant="body2">
        Try adjusting your filters or search term
      </Typography>
    </Box>
  );
};

/**
 * 
 * @param {React.ReactNode} renderItem (optional) custom item component that accepts `mapLayer` as the only param 
 * @returns 
 */
export const MapList = ({ maps, renderItem }) => {
  if (maps.length === 0) {
    return <EmptyMapList />;
  }

  return (
    <Box sx={{ overflow: "auto" }}>
      {maps.sort((a, b) => a.map.name.localeCompare(b.map.name)).map((mapLayer) => (
        renderItem ? renderItem(mapLayer) : <MapListItem key={mapLayer.id} mapLayer={mapLayer} />
      ))}
    </Box>
  );
};
