import { cmd } from "@/utils/fetchUtils";
import { useLoaderData } from "react-router-dom";
import PlayersTable from "./game-table";
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  getExpandedRowModel,
} from "@tanstack/react-table";
import { columns } from "./game-columns";
import { useMemo, useState } from "react";
import dayjs from "dayjs";
import { Typography, Box, Paper } from "@mui/material";
import Grid from "@mui/material/Grid2"

export const loader = async ({ params }) => {
  return await cmd.GET_COMPLETED_GAME_DETAIL({
    params: { map_id: params.gameId },
  });
};

const StatCard = ({ playerStats, statsKey }) => {
    const title = statsKey.replace("_", " ").toUpperCase();
    return (
        <Grid size={{ xs: 12, sm: 6, md: 4, lg: "auto" }}>
            <Paper sx={{ p: 2 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>TOP {title}</Typography>
                {playerStats
                    .sort((a, b) => b[statsKey] - a[statsKey])
                    .slice(0, 5)
                    .map((player, i) => (
                        <Box key={player.player_id} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">
                                {i === 0 ? `🥇 ${player.player}` : i === 1 ? `🥈 ${player.player}` : i === 2 ? `🥉 ${player.player}` : player.player}
                            </Typography>
                            <Box sx={{ flexGrow: 1, minWidth: 10 }} />
                            <Typography variant="body2" color="primary">{player[statsKey]}</Typography>
                        </Box>
                    ))}
            </Paper>
        </Grid>
    );
};

const GameDetailsPage = () => {
  const data = useLoaderData();
  const [playersRowSelection, setPlayersRowSelection] = useState({});

  const table = useReactTable({
    data: data.player_stats,
    columns: columns,
    getRowCanExpand: () => true,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onRowSelectionChange: setPlayersRowSelection,
    getExpandedRowModel: getExpandedRowModel(),
    getRowId: (row) => row.player_id,
    initialState: {
      pagination: {
        pageIndex: 0,
        pageSize: 100,
      },
    },
    state: {
      rowSelection: playersRowSelection,
    },
  });

  const selectedPlayers = useMemo(() => {
    return Object.keys(playersRowSelection)
      .map((key) => {
        return (
          table.getSelectedRowModel().rows.find((row) => row.id === key)
            ?.original ?? null
        );
      })
      .filter(Boolean)
      .map((playerRow) => ({ player_id: playerRow.player_id, name: playerRow.player }));
  }, [playersRowSelection, table.getSelectedRowModel().rows]);

  return (
    <div>
      <Box sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Box>
            <Typography variant="h4" sx={{ mb: 2 }}>
              {data.map.pretty_name}
            </Typography>
            {data.result && (
              <Typography variant="h5" sx={{ color: 'text.secondary' }}>
                Score: <Box component="span" sx={{ color: 'primary.main' }}>Allies {data.result.allied}</Box> : <Box component="span" sx={{ color: 'error.main' }}>{data.result.axis} Axis</Box>
              </Typography>
            )}
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              {dayjs(data.start).format("HH:mm, MMM D, YYYY")}
            </Typography>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              Duration: {dayjs.duration(dayjs(data.end) - dayjs(data.start)).format("HH:mm")}
            </Typography>
            <Typography variant="subtitle2" color="text.secondary">
              Game ID: {data.id}
            </Typography>
          </Box>
        </Box>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <StatCard playerStats={data.player_stats} statsKey="kills" />
          <StatCard playerStats={data.player_stats} statsKey="combat" />
          <StatCard playerStats={data.player_stats} statsKey="support" />
          <StatCard playerStats={data.player_stats} statsKey="offense" />
          <StatCard playerStats={data.player_stats} statsKey="defense" />
          <StatCard playerStats={data.player_stats} statsKey="kills_streak" />
        </Grid>
        <PlayersTable table={table} selectedPlayers={selectedPlayers} />
      </Box>
    </div>
  );
};

export default GameDetailsPage;
