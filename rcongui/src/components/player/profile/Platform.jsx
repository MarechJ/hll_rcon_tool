import React from "react";
import {
  faSteam,
  faXbox,
  faPlaystation,
} from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import FortIcon from "@mui/icons-material/Fort";
import VideogameAssetIcon from '@mui/icons-material/VideogameAsset';
import { Box, Chip } from "@mui/material";
import { getSteamProfileUrl } from "@/utils/lib";

function PlatformChip({ platform, playerId }) {
  if (platform === "steam") {
    return (
      <Chip
        component={"a"}
        href={getSteamProfileUrl(playerId)}
        target="_blank"
        rel="noreferrer"
        icon={<Box sx={{ width: 14, height: 24 }}><FontAwesomeIcon icon={faSteam} size="xs" /></Box>}
        label="Steam"
        sx={{ "&:hover": { cursor: "pointer" } }}
      />
    );
  }
  if (platform === "epic") {
    return <Chip icon={<FortIcon />} label="Epic" />;
  }
  if (platform === "xbl" || platform === "xsx") {
    return <Chip icon={<Box sx={{ width: 14, height: 24 }}><FontAwesomeIcon icon={faXbox} size="xs" /></Box>} label="Xbox" />;
  }
  if (platform === "psn" || platform === "ps5") {
    return (
      <Chip
        icon={<Box sx={{ width: 14, height: 24 }}><FontAwesomeIcon icon={faPlaystation} size="xs" /></Box>}
        label="PlayStation"
      />
    );
  }
  if (platform) {
    return <Chip icon={<VideogameAssetIcon />} label={platform} />;
  }

  return <Chip icon={<VideogameAssetIcon />} label={"unset"} />;
}

export default PlatformChip;
