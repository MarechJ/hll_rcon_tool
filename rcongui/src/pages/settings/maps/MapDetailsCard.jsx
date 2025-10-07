// Component for displaying a map name, image, and description

import { Typography, Box, Stack } from "@mui/material";
import CopyableText from "@/components/shared/CopyableText";
import { getMapLayerImageSrc, unifiedGamemodeName } from "./objectives/helpers";

export function MapDetailsCard({ mapLayer }) {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 2,
        letterSpacing: 0.85,
        flexGrow: 1,
      }}
    >
      <Box
        component="img"
        src={getMapLayerImageSrc(mapLayer)}
        alt={mapLayer.map.pretty_name}
        sx={{ width: 48, height: 32, borderRadius: 1, objectFit: "cover" }}
      />
      <Stack direction={"row"} flexWrap={"wrap"} alignItems={"center"}>
        <Typography
          sx={{ width: { xs: "100%", md: "175px" } }}
          fontWeight="medium"
        >
          <CopyableText
            text={mapLayer.id}
            label={mapLayer.map.pretty_name}
            sx={{ p: 0, m: 0 }}
          />
        </Typography>
        <Stack direction={"row"} flexWrap={"wrap"}>
          <Stack
            direction={"row"}
            alignItems={"center"}
            spacing={1}
            sx={{
              flexGrow: 1,
              minWidth: 150,
              width: { xs: "100%", sm: "auto" },
            }}
          >
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ textTransform: "uppercase", fontSize: 12 }}
            >
              {unifiedGamemodeName(mapLayer.game_mode)}{" "}
              {unifiedGamemodeName(mapLayer.game_mode) === "offensive" &&
                `(${mapLayer.attackers})`}
            </Typography>
          </Stack>
          <Stack
            direction={"row"}
            alignItems={"center"}
            spacing={1}
            sx={{ width: { xs: "100%", sm: "auto" }, px: { xs: 0, md: 1 } }}
          >
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ textTransform: "uppercase", fontSize: 12 }}
            >
              {mapLayer.environment}
            </Typography>
          </Stack>
        </Stack>
      </Stack>
    </Box>
  );
}

export function MapDetailsCardCompact({ mapLayer }) {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 2,
        letterSpacing: 0.85,
        flexGrow: 1,
      }}
    >
      <Box
        component="img"
        src={getMapLayerImageSrc(mapLayer)}
        alt={mapLayer.map.pretty_name}
        sx={{ width: 48, height: 32, borderRadius: 1, objectFit: "cover" }}
      />
      <Stack sx={{ textTransform: "uppercase" }}>
        <Typography fontWeight="medium" fontSize={12}>
          <CopyableText
            text={mapLayer.id}
            label={mapLayer.map.pretty_name}
            sx={{ p: 0, m: 0 }}
          />
        </Typography>
        <Stack direction={"row"} gap={2}>
          <Typography variant="body2" color="text.secondary" fontSize={12}>
            {unifiedGamemodeName(mapLayer.game_mode)}{" "}
            {unifiedGamemodeName(mapLayer.game_mode) === "offensive" &&
              `(${mapLayer.attackers})`}
          </Typography>
          <Typography variant="body2" color="text.secondary" fontSize={12}>
            {mapLayer.environment}
          </Typography>
        </Stack>
      </Stack>
    </Box>
  );
}
