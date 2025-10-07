import { Skeleton, Stack, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";
import { useQuery } from "@tanstack/react-query";
import { gameQueryOptions } from "@/queries/game-query";
import dayjs from "dayjs";
import { useGlobalStore } from "@/stores/global-state";

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
  const serverState = useGlobalStore((state) => state.status)
  const gameState = useGlobalStore((state) => state.gameState)
  const name = serverState?.short_name ?? "<Server Name>";
  const numCurrentPlayers = serverState?.current_players ?? 0;
  const maxPlayers = serverState?.max_players ?? 100;
  const mapName = gameState?.current_map?.pretty_name ?? "Unknown Map";
  const timeRemaining = dayjs
    .duration(gameState?.time_remaining ?? 0, "seconds")
    .format("HH:mm:ss");
  const balance = `${gameState?.num_allied_players ?? 0}vs${
    gameState?.num_axis_players ?? 0
  }`;
  const score = `${gameState?.allied_score ?? 0}:${gameState?.axis_score ?? 0}`;

  if (!(serverState && gameState)) {
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
