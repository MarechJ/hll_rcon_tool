import { Avatar, Box, Divider, Typography } from "@mui/material";
import { getMapLayerImageSrc, unifiedGamemodeName } from "./helpers";
import { styled } from "@mui/material/styles"

const Wrapper = styled('div')(({ theme }) => ({
  display: "flex",
  flexWrap: "wrap",
  gap: theme.spacing(0.5),
  textTransform: "capitalize",
}));

export function MapDetails({ mapLayer }) {
  const gameMode = unifiedGamemodeName(mapLayer.game_mode)

  return (
    <Wrapper>
      <Typography variant="caption">{gameMode}</Typography>
      {gameMode === "offensive" && (
        <>
          <Divider orientation="vertical" flexItem />
          <Typography variant="caption">{mapLayer.attackers}</Typography>
        </>
      )}
      <Divider orientation="vertical" flexItem />
      <Typography variant="caption">{mapLayer.environment}</Typography>
    </Wrapper>
  );
}

export function MapAvatar({ mapLayer }) {
  return (
    <Avatar src={getMapLayerImageSrc(mapLayer)} />
  )
}
