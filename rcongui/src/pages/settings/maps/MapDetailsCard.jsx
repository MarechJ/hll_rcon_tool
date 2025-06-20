// Component for displaying a map name, image, and description

import { getMapLayerImageSrc } from "@/components/MapManager/helpers";
import { Typography, Box } from "@mui/material";
import CopyableText from "@/components/shared/CopyableText";
import { map } from "lodash";

export function MapDetailsCard({ mapLayer }) {
  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 2, letterSpacing: 0.85 }}>
      <Box
        component="img"
        src={getMapLayerImageSrc(mapLayer)}
        alt={mapLayer.map.pretty_name}
        sx={{ width: 48, height: 48, borderRadius: 1, objectFit: "cover" }}
      />
      <Box>
        <Typography fontWeight="medium" lineHeight={0.75}>
          <CopyableText text={mapLayer.id} label={mapLayer.map.pretty_name} sx={{ p: 0, m: 0 }} />
        </Typography>
        <Box sx={{ display: "flex", flexDirection: "column" }} lineHeight={0.75}>
          <Typography variant="body2" color="text.secondary">
            {mapLayer.game_mode} {mapLayer.game_mode === "offensive" && `(${mapLayer.attackers} -> ${mapLayer.attackers === "axis" ? "allies" : "axis"})`}
          </Typography>
          <Typography variant="body2" color="text.secondary" lineHeight={0.75}>
            {mapLayer.environment}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
