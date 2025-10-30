import { levelToRank, toSnakeCase } from "@/utils/lib";
import { Avatar, Chip } from "@mui/material";
import MilitaryTechIcon from '@mui/icons-material/MilitaryTech';
import React from "react";
import EditSoldierButton from "./EditSoldierButton";

function LevelChip({ level, playerId, currentSoldierData }) {
  if (!level) {
    return <EditSoldierButton Icon={MilitaryTechIcon} playerId={playerId} currentSoldierData={currentSoldierData} />
  }
  return (
    <Chip
      avatar={
        <Avatar
          alt={`Level ${level}`}
          src={`/icons/ranks/${toSnakeCase(levelToRank(level))}.webp`}
        />
      }
      label={level}
    />
  );
}

export default LevelChip;
