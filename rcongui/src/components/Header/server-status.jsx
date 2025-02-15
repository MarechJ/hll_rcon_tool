import { useEffect } from "react";
import { Skeleton, Stack, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";
import { useQuery } from "@tanstack/react-query";
import { gameQueryOptions } from "@/queries/game-query";
import dayjs from "dayjs";

const Wrapper = styled("div")(({ theme }) => ({
  color: theme.palette.text.primary,
  textOverflow: "ellipsis",
  textWrap: "nowrap",
  textAlign: "left",
  paddingLeft: theme.spacing(1),
  paddingRight: theme.spacing(1),
  [theme.breakpoints.up("lg")]: {
    textAlign: "center",
    padding: theme.spacing(1),
    textWrap: "wrap",
  },
}));

const ServerStatus = ({ compact }) => {
  const { data: status, isLoading } = useQuery({
    ...gameQueryOptions.publicState(),
  });

  const name = status?.name?.short_name ?? "<Server Name>";
  const numCurrentPlayers = status?.player_count ?? 0;
  const maxPlayers = status?.max_player_count ?? 100;
  const mapName = status?.current_map?.map?.pretty_name ?? "Unknown Map";
  const timeRemaining = dayjs
    .duration(status?.time_remaining ?? 0, "seconds")
    .format("HH:mm:ss");
  const balance = `${status?.player_count_by_team?.allied ?? 0}vs${
    status?.player_count_by_team?.axis ?? 0
  }`;
  const score = `${status?.score?.allied ?? 0}:${status?.score?.axis ?? 0}`;

  useEffect(() => {
    document.title = `${
      status?.name?.short_name ?? "<Server Name>"
    } | ${timeRemaining} | ${mapName} (${numCurrentPlayers})`;
  }, [status]);

  if (isLoading) {
    return (
      <Wrapper>
        <Stack
          sx={{
            alignItems: { xs: "flex-start", lg: "center" },
            gap: { xs: 0, lg: 0.5 },
          }}
        >
          <Skeleton variant="text" width={100} height={16} />
          <Skeleton variant="text" width={compact ? 160 : 60} height={16} />
          {!compact && <Skeleton variant="text" width={60} height={16} />}
        </Stack>
      </Wrapper>
    );
  }

  return compact ? (
    <Wrapper sx={{ textAlign: "left" }}>
      <Typography variant="subtitle2">{name}</Typography>
      <Typography variant="caption">
        {numCurrentPlayers}/{maxPlayers} ({balance}) - {mapName} -{" "}
        {timeRemaining} - {score}
      </Typography>
    </Wrapper>
  ) : (
    <Wrapper>
      <Typography variant="subtitle2">{name}</Typography>
      <Typography variant="caption">
        {numCurrentPlayers}/{maxPlayers} ({balance}) - {timeRemaining}
      </Typography>
      <Typography component={"div"} variant="caption">
        {score} - {mapName}
      </Typography>
    </Wrapper>
  );
};

export default ServerStatus;
