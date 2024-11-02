import React, { useMemo, useState } from "react";
import Grid from "@mui/material/Grid2";
import { cmd } from "@/utils/fetchUtils";
import { columns } from "./players-columns";
import { Header } from "@/components/game/Header";
import { extractPlayers, extractTeamState } from "@/utils/extractPlayers";
import { useLoaderData } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import PlayersTable from "./players-table";
import LogsTable from "./logs-table";
import { logsColumns } from "./logs-columns";
import { useStorageState } from "@/hooks/useStorageState";
import { Button, Stack } from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import teamViewResponse from "./data.json";
import { teamsLiveQueryOptions } from "@/queries/teams-live-query";
import { normalizePlayerProfile } from "@/utils/lib";
import { useReactTable } from "@tanstack/react-table";
import {
  getCoreRowModel,
  getExpandedRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";
import { Box, IconButton } from "@mui/material";
import { DebouncedSearchInput, TeamSelectionToolbar } from "./players-filters";
import SettingsIcon from "@mui/icons-material/Settings";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { playerGameActions } from "@/features/player-action/actions";

const limitOptions = [
  100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000,
];

const interval = 15 * 1000; // 15 seconds

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
  const [tableSize, setTableSize] = useState("small");
  const [playersVisible, setPlayersVisible] = useState(true);
  const [logsVisible, setLogsVisible] = useState(true);

  const [sorting, setSorting] = useState([]);
  const [rowSelection, setRowSelection] = useState({});
  const [columnFilters, setColumnFilters] = useState([]);

  // const { data: teamData } = useQuery({
  //   ...teamsLiveQueryOptions,
  //   staleTime: 5 * 1000,
  //   refetchInterval: 10 * 1000,
  // });

  const teamData = teamViewResponse.result;

  const { data: gameState } = useQuery({
    queryKey: ["game", "state"],
    queryFn: cmd.GET_GAME_STATE,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

  const playersData = React.useMemo(() => {
    if (!teamData) return [];
    return extractPlayers(teamData).map((player) => ({
      ...player,
      profile: normalizePlayerProfile(player?.profile),
    }));
  }, [teamData]);

  // Using custom hook that synchronizes the components state
  // and the browser's local storage
  const [logsConfig, setLogsConfig] = useStorageState("logs-config", {
    players: [],
    actions: [],
    inclusive: true,
    limit: 500,
    highlighted: false,
    tableMode: "table",
  });

  // Use React Query to manage background refetching
  const {
    data: logsView,
    error,
    isLoading,
  } = useQuery({
    queryKey: ["logs", "live"],
    queryFn: () =>
      cmd.GET_RECENT_LOGS({
        params: {
          end: logsConfig.limit,
          filter_action: logsConfig.actions,
          filter_player: logsConfig.players,
          inclusive_filter: logsConfig.inclusive,
        },
      }),
    initialData: initialLogsView,
    refetchInterval: interval, // Polling interval for updates
  });

  const playersTable = useReactTable({
    data: playersData,
    columns,
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getCoreRowModel: getCoreRowModel(),
    onRowSelectionChange: setRowSelection,
    onColumnFiltersChange: setColumnFilters,
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getExpandedRowModel: getExpandedRowModel(),
    getRowId: (row) => row.player_id,
    state: {
      sorting,
      rowSelection,
      columnFilters,
    },
  });

  // const logsData = React.useMemo(() => {
  //   if (!logsView || !logsView.logs) {
  //     return [];
  //   }

  //   return logsView.logs.map((log, index) => ({
  //     id: index,
  //     time: log.event_time ?? "N/A", // Handle missing fields gracefully
  //     action: log.action ?? "N/A",
  //     player: log.player_name_1 ?? "N/A",
  //     content: log.sub_content ?? "",
  //   }));
  // }, [logsView]);

  const handleFiltersChange = (newParams) => {
    setLogsConfig((prevConfig) => ({
      ...prevConfig,
      ...newParams,
    }));
  };

  const gameData = React.useMemo(() => {
    if (gameState && teamData) {
      return {
        ...gameState,
        allies: {
          ...extractTeamState(teamData?.allies ?? {}),
          ...(teamData?.allies ?? {}),
        },
        axis: {
          ...extractTeamState(teamData?.axis ?? {}),
          ...(teamData?.axis ?? {}),
        },
      };
    }
    return null;
  }, [gameState, teamData]);

  const selectedPlayers = useMemo(() => {
    return Object.keys(rowSelection)
      .map((key) => {
        return (
          playersTable.getSelectedRowModel().rows.find((row) => row.id === key)
            ?.original ?? null
        );
      })
      .filter(Boolean);
  }, [rowSelection, playersTable.getSelectedRowModel().rows]);

  return (
    <Grid container spacing={1}>
      <Grid size={12}>
        <Header data={gameData} />
      </Grid>
      {/* <Grid size={12}>
        <Button onClick={() => setTableSize("small")}>Small</Button>
        <Button onClick={() => setTableSize("medium")}>Medium</Button>
        <Button onClick={() => setTableSize("large")}>Large</Button>
        <Button startIcon={playersVisible ? <VisibilityIcon /> : <VisibilityOffIcon />} onClick={() => setPlayersVisible(!playersVisible)}>
          {playersVisible ? "Hide Players" : "Show Players"}
        </Button>
        <Button startIcon={logsVisible ? <VisibilityIcon /> : <VisibilityOffIcon />} onClick={() => setLogsVisible(!logsVisible)}>
          {logsVisible ? "Hide Logs" : "Show Logs"}
        </Button>
      </Grid> */}
      {playersVisible && (
        <Grid
          size={{
            xs: 12,
            lg: "auto",
          }}
        >
          <TeamSelectionToolbar table={playersTable} teamData={teamData} />
          <Stack direction="column" spacing={0}>
            <Stack
              direction="row"
              spacing={1}
              sx={{
                borderRadius: 0,
                border: (theme) => `1px solid ${theme.palette.divider}`,
                borderBottom: "none",
              }}
            >
              <ActionMenuButton
                actions={playerGameActions}
                disabled={
                  !playersTable.getIsSomePageRowsSelected() &&
                  !playersTable.getIsAllRowsSelected()
                }
                recipients={selectedPlayers}
                orientation="horizontal"
                disableRipple={true}
                sx={{
                  p: "1px 4px",
                  height: "100%",
                }}
              />
              <DebouncedSearchInput
                initialValue={
                  playersTable.getColumn("name")?.getFilterValue() ?? ""
                }
                onChange={(value) => {
                  playersTable.getColumn("name")?.setFilterValue(value);
                }}
              />
              <IconButton size="small" sx={{ p: 0.5, borderRadius: 0 }}>
                <SettingsIcon sx={{ fontSize: 16 }} />
              </IconButton>
            </Stack>
            <Box
              sx={{
                overflowX: "auto",
                overflowY: "hidden",
                width: "100%",
                scrollbarWidth: "none",
              }}
            >
              <PlayersTable table={playersTable} size={tableSize} />
            </Box>
          </Stack>
        </Grid>
      )}
      {logsVisible && (
        <Grid
          size={{
            xs: 12,
            lg: "grow",
          }}
        >
          <LogsTable
            data={logsView.logs}
            columns={logsColumns}
            size={tableSize}
          />
        </Grid>
      )}
    </Grid>
  );
};

export default Live;
