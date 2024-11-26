import { cmd } from "@/utils/fetchUtils";
import { useLoaderData } from "react-router-dom";
import {
  Stack,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import { gameQueryOptions } from "@/queries/game-query";
import { useQuery } from "@tanstack/react-query";
import { Board } from "@/components/game/Board";
import dayjs from "dayjs";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { VoteStatus } from "@/pages/settings/map-manager/votemap/vote-status";
import { columns } from "./public-game-columns";
import { StatCard } from "@/pages/stats/games/[gameId]";
import PlayersTable from "./public-game-table";
import { useReactTable } from "@tanstack/react-table";
import {
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  getExpandedRowModel,
} from "@tanstack/react-table";
import { useMemo } from "react";

export const loader = async () => {
  const stats = await cmd.GET_LIVE_GAME();
  const game = await cmd.GET_PUBLIC_GAME_STATE();
  const session = await cmd.GET_LIVE_SESSIONS();
  return { stats, game, session };
};

const LiveGamePage = () => {
  const initialData = useLoaderData();

  const {
    data: { stats },
    isLoading: statsIsLoading,
  } = useQuery({
    ...gameQueryOptions.live(),
    initialData: initialData.stats,
  });

  const { data: game, isLoading: gameIsLoading } = useQuery({
    ...gameQueryOptions.publicState(),
    initialData: initialData.game,
  });

  const {
    data: { stats: sessions },
    isLoading: sessionIsLoading,
  } = useQuery({
    ...gameQueryOptions.sessions(),
    initialData: initialData.session,
  });

  const tableData = useMemo(() => stats.map((stat) => {
    if (!sessions || !stats) return [];
    if (!sessions) return stats;

    return ({
        ...stat,
        is_online: !!sessions.find((s) => s.player_id === stat.player_id),
      })
    }),
    [stats, sessions],
  );

  const table = useReactTable({
    data: tableData,
    columns: columns,
    getRowCanExpand: () => true,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    getRowId: (row) => row.player_id,
    initialState: {
      pagination: {
        pageIndex: 0,
        pageSize: 100,
      },
      sorting: [{ id: "time", desc: true }],
    },
  });

  if (statsIsLoading || gameIsLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Stack gap={3}>
      <section id="game-board">
        <Board
          data={{
            // convert seconds to "HH:mm:ss"
            raw_time_remaining: dayjs
              .duration(game.time_remaining, "seconds")
              .format("HH:mm:ss"),
            allied_score: game.score.allied,
            axis_score: game.score.axis,
            current_map: game.current_map.map,
            num_allied_players: game.player_count_by_team.allied,
            num_axis_players: game.player_count_by_team.axis,
          }}
        />
      </section>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Vote Map Status</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <VoteStatus voteStatus={game.vote_status} />
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Player Statistics</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <StatCard playerStats={stats} statsKey="kills" />
            <StatCard playerStats={stats} statsKey="combat" />
            <StatCard playerStats={stats} statsKey="support" />
            <StatCard playerStats={stats} statsKey="offense" />
            <StatCard playerStats={stats} statsKey="defense" />
            <StatCard playerStats={stats} statsKey="kills_streak" />
          </Grid>
        </AccordionDetails>
      </Accordion>

      <section id="players-table">
        <PlayersTable table={table} />
      </section>
    </Stack>
  );
};

export default LiveGamePage;
