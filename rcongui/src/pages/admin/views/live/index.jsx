import React from "react";
import Grid from "@mui/material/Grid2";
import GameLogs from "@/components/LiveLogs";
import { cmd } from "@/utils/fetchUtils";
// import PlayersTable, { playerToRow } from "./players-table";
import { columns } from "./PlayersTable";
import { Header } from "@/components/game/Header";
import { extractPlayers, extractTeamState } from "@/utils/extractPlayers";
import { useLoaderData } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import PlayersTable from "./PlayersTable";
// import teamViewResponse from "./data.json"

export const loader = async () => {
  const logs = await cmd.GET_LIVE_LOGS({
    params: {
      end: 100,
      filter_action: [],
      filter_player: [],
      inclusive_filter: true,
    },
  });

  return { initialLogsView: logs };
};

const Live = () => {
  const { initialLogsView } = useLoaderData();

  const { data: teamData } = useQuery({
    queryKey: ["teams", "live"],
    queryFn: cmd.GET_LIVE_TEAMS,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

  // const teamData = teamViewResponse.result;

  const { data: gameState } = useQuery({
    queryKey: ["game", "state"],
    queryFn: cmd.GET_GAME_STATE,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

  const tableData = React.useMemo(() => {
    if (!teamData) return [];
    return extractPlayers(teamData);
  }, [teamData]);

  const gameStateProp = React.useMemo(() => {
    if (gameState && teamData) {
      return {
        ...gameState,
        allies: extractTeamState(teamData?.allies ?? {}),
        axis: extractTeamState(teamData?.axis ?? {}),
      };
    }
    return null;
  }, [gameState, teamData]);

  return (
    <Grid container spacing={1}>
      <Grid size={12}>
        <Header teamData={teamData} gameState={gameStateProp} />
      </Grid>
      <Grid
        size={{
          sm: 12,
          lg: "auto",
        }}
      >
        <PlayersTable columns={columns} data={tableData} />
      </Grid>
      <Grid
        size={{
          sm: 12,
          lg: "grow",
        }}
      >
        <GameLogs initialLogsView={initialLogsView} />
      </Grid>
    </Grid>
  );
};

export default Live;
