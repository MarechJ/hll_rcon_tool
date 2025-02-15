import { useQuery } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";
import {
  Box,
  Typography,
} from "@mui/material";
import { MapAvatar } from "@/components/MapManager/map-details";
import ScrollableCard from "@/components/shared/card/ScrollableCard";

const MapRotationCard = () => {
  const { data: mapRotation = [] } = useQuery({
    queryKey: ["map-rotation"],
    queryFn: async () => await cmd.GET_MAP_ROTATION(),
  });

  return (
    <ScrollableCard sx={{ height: "100%" }} title="Map Rotation">
      <Box component="ol" sx={{ listStylePosition: "inside", pl: 0 }}>
        {mapRotation.map((map) => (
          <Box
            component="li"
            key={map.id}
            sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.25 }}
          >
            <MapAvatar mapLayer={map} sx={{ width: 24, height: 24 }} />
            <Typography variant="subtitle2">{map.pretty_name}</Typography>
          </Box>
        ))}
      </Box>
    </ScrollableCard>
  );
};

export default MapRotationCard; 