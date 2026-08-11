import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import VideogameAssetIcon from "@mui/icons-material/VideogameAsset";
import { Box, Chip } from "@mui/material";
import { getSteamProfileUrl } from "@/utils/lib";
import EditSoldierButton from "./EditSoldierButton";
import {
  getPlatformIcon,
  getPlatformLabel,
} from "@/constants/platforms";

function PlatformChip({ platform, playerId, currentSoldierData }) {
  if (!platform)
    return (
      <EditSoldierButton
        Icon={VideogameAssetIcon}
        playerId={playerId}
        currentSoldierData={currentSoldierData}
      />
    );

  const icon = (
    <Box sx={{ width: 14, height: 24 }}>
      <FontAwesomeIcon icon={getPlatformIcon(platform)} size="xs" />
    </Box>
  );

  if (platform === "steam") {
    return (
      <Chip
        component={"a"}
        href={getSteamProfileUrl(playerId)}
        target="_blank"
        rel="noreferrer"
        icon={icon}
        label={getPlatformLabel(platform)}
        sx={{ "&:hover": { cursor: "pointer" } }}
      />
    );
  }

  return <Chip icon={icon} label={getPlatformLabel(platform)} />;
}

export default PlatformChip;
