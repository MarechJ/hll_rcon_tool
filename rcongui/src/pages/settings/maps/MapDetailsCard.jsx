// Component for displaying a map name, image, and description

import { getMapLayerImageSrc } from "@/components/MapManager/helpers";
import { Typography, Box } from "@mui/material";
import CopyableText from "@/components/shared/CopyableText";

export function MapDetailsCard({ mapLayer }) {
  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
      <Box
        component="img"
        src={getMapLayerImageSrc(mapLayer)}
        alt={mapLayer.map.pretty_name}
        sx={{ width: 48, height: 48, borderRadius: 1, objectFit: "cover" }}
      />
      <Box>
        <Typography variant="body1" fontWeight="medium">
          <CopyableText text={mapLayer.id} label={mapLayer.map.pretty_name} />
        </Typography>
        <Box sx={{ display: "flex", gap: 1, mt: 0.5 }}>
          <Typography variant="body2" color="text.secondary">
            {mapLayer.game_mode}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {mapLayer.environment}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
