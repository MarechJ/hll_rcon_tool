import React, { useEffect } from "react";
import { Typography } from "@mui/material";
import { styled } from "@mui/material/styles";
import { useGlobalStore } from "@/hooks/useGlobalState";

const Wrapper = styled("div")(({ theme }) => ({
  paddingLeft: theme.spacing(1),
  color: theme.palette.text.primary,
  overflowX: "hidden",
  textOverflow: "ellipsis",
  textWrap: "nowrap",
}));

const MenuBox = styled("div")(({ theme }) => ({
  display: "flex",
  gap: theme.spacing(1),
}));

const ServerStatus = () => {
  const status = useGlobalStore((state) => state.status);
  const gameState = useGlobalStore((state) => state.gameState);

  const name = status?.name ?? "Loading...";
  const numCurrentPlayers = status?.current_players ?? 0;
  const maxPlayers = status?.max_players ?? 100;
  const mapName = gameState?.current_map?.pretty_name ?? "Unknown Map";
  const timeRemaining = gameState?.raw_time_remaining ?? "0:00:00";
  const balance = `${gameState?.num_allied_players ?? 0}vs${
    gameState?.num_axis_players ?? 0
  }`;
  const score = `${gameState?.allied_score ?? 0}:${gameState?.axis_score ?? 0}`;

  useEffect(() => {
    document.title = `(${numCurrentPlayers}) ${status?.short_name ?? "<Server Name>"}`;
  }, [status]);

  return (
    <Wrapper>
      <MenuBox>
        <Typography variant="subtitle2">
          {name}
        </Typography>
      </MenuBox>
      <Typography variant="caption">
        {numCurrentPlayers}/{maxPlayers} ({balance}) - {mapName} -{" "}
        {timeRemaining} - {score}
      </Typography>
    </Wrapper>
  );
};

export default ServerStatus;
