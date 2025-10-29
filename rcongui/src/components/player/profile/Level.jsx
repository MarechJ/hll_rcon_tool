import { levelToRank, toSnakeCase } from "@/utils/lib";
import { Avatar, Chip } from "@mui/material";
import MilitaryTechIcon from '@mui/icons-material/MilitaryTech';
import React from "react";

function LevelChip({ level }) {
  if (!level) {
    return (
      <Chip
        icon={<MilitaryTechIcon />}
        label={"unset"}
        variant="outlined"
        size="small"
      />
    );
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
