import React, { useEffect } from "react";
import { Typography } from "@mui/material";
import { styled } from "@mui/material/styles";
import { useQuery } from "@tanstack/react-query";
import { gameQueryOptions } from "@/queries/game-query";
import dayjs from "dayjs";

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
  const { data: status, isLoading } = useQuery({
    ...gameQueryOptions.publicState(),
    placeholderData: {
      name: {
        name: "Loading...",
        short_name: "Loading..."
      },
      current_map: {
        pretty_name: "Unknown Map"
      },
      raw_time_remaining: "0:00:00",
      num_allied_players: 0,
      num_axis_players: 0,
      allied_score: 0,
      axis_score: 0,
    }
  })

  const name = isLoading ? "Loading..." : status?.name?.name ?? "Something went wrong";
  const numCurrentPlayers = status?.player_count ?? 0;
  const maxPlayers = status?.max_player_count ?? 100;
  const mapName = status?.current_map?.map?.pretty_name ?? "Unknown Map";
  const timeRemaining = dayjs.duration(status?.time_remaining ?? 0, "seconds").format("HH:mm:ss");
  const balance = `${status?.player_count_by_team?.allied ?? 0}vs${
    status?.player_count_by_team?.axis ?? 0
  }`;
  const score = `${status?.score?.allied ?? 0}:${status?.score?.axis ?? 0}`;

  useEffect(() => {
    document.title = `${timeRemaining} | ${mapName} (${numCurrentPlayers}) | ${status?.name?.name ?? "<Server Name>"}`;
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
