import { CompletedGameDetails, StatCard } from "@/pages/stats/games/[gameId]";
import { columns } from "@/public-pages/public-game-columns";
import PlayersTable from "@/public-pages/public-game-table";
import { cmd } from "@/utils/fetchUtils";
import { Box } from "@mui/material";
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  getExpandedRowModel,
} from "@tanstack/react-table";
import { useLoaderData } from "react-router-dom";
import Grid from "@mui/material/Grid2";


export const loader = async ({ params }) => {
  return await cmd.GET_COMPLETED_GAME_DETAIL({
    params: { map_id: params.gameId },
  });
};

const gameColumns = columns.filter((column) => column.id !== "online-status");

const CompletedGamePage = () => {
  const data = useLoaderData();

  const table = useReactTable({
    data: data.player_stats,
    columns: gameColumns,
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

  return (
    <div>
      <Box sx={{ p: 4 }}>
        <CompletedGameDetails
          mapLayer={data.map}
          result={data.result}
          start={data.start}
          end={data.end}
          id={data.id}
        />
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <StatCard playerStats={data.player_stats} statsKey="kills" />
          <StatCard playerStats={data.player_stats} statsKey="combat" />
          <StatCard playerStats={data.player_stats} statsKey="support" />
          <StatCard playerStats={data.player_stats} statsKey="offense" />
          <StatCard playerStats={data.player_stats} statsKey="defense" />
          <StatCard playerStats={data.player_stats} statsKey="kills_streak" />
        </Grid>
        <PlayersTable table={table} />
      </Box>
    </div>
  );
};

export default CompletedGamePage;
