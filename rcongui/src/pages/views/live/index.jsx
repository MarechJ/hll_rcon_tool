import { useEffect, useMemo, useState } from "react";
import { cmd } from "@/utils/fetchUtils";
import { columns as playersColumns } from "./players-columns";
import { Header } from "@/components/game/Header";
import { extractPlayers, extractTeamState } from "@/utils/extractPlayers";
import { useLoaderData } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import PlayersTable from "./players-table";
import LogsTable from "./logs-table";
import { logsColumns } from "./logs-columns";
import { useStorageState } from "@/hooks/useStorageState";
import { teamsLiveQueryOptions } from "@/queries/teams-live-query";
import { normalizePlayerProfile } from "@/utils/lib";
import {
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import Grid from "@mui/material/Grid2";
import localStorageConfig from "@/config/localStorage";

const interval = 15 * 1000; // 15 seconds

export const loader = async () => {
  const response = await cmd.GET_LIVE_LOGS({
    payload: {
      end: 250,
      filter_action: [],
      filter_player: [],
      inclusive_filter: true,
    },
  });

  return { initialLogsView: response };
};

const Live = () => {
  // ---------------- VIEW STATE -----------------
  const { initialLogsView } = useLoaderData();

  // ---------------- PLAYERS DATA -----------------
  const { data: teamData } = useQuery({
    ...teamsLiveQueryOptions,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

  // const teamData = teamViewResponse.result;

  const playersData = useMemo(() => {
    if (!teamData) return [];
    return extractPlayers(teamData).map((player) => ({
      ...player,
      profile: normalizePlayerProfile(player?.profile ?? {}),
    }));
  }, [teamData]);

  // ---------------- LOGS DATA -----------------
  // Using custom hook that synchronizes the components state
  // and the browser's local storage
  const [logsSearchParams, setLogsSearchParams] = useStorageState(
    localStorageConfig.LIVE_LOGS_SEARCH_PARAMS.key,
    localStorageConfig.LIVE_LOGS_SEARCH_PARAMS.defaultValue
  );

  const { data: logsView } = useQuery({
    queryKey: [
      "logs",
      "live",
      {
        end: logsSearchParams.limit,
        filter_action: logsSearchParams.actions,
        filter_player: logsSearchParams.players,
        inclusive_filter: logsSearchParams.inclusive_filter,
      },
    ],
    queryFn: () =>
      cmd.GET_LIVE_LOGS({
        payload: {
          end: logsSearchParams.limit,
          filter_action: logsSearchParams.actions,
          filter_player: logsSearchParams.players,
          inclusive_filter: logsSearchParams.inclusive_filter,
        },
      }),
    select: (response) => response.result,
    initialData: initialLogsView,
    refetchInterval: interval, // Polling interval for updates
  });

  // ---------------- GAME HEADER DATA -----------------
  const { data: gameState } = useQuery({
    queryKey: ["game", "state"],
    queryFn: cmd.GET_GAME_STATE,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

  const gameData = useMemo(() => {
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

  // ---------------- PLAYERS TABLE STATE -----------------
  const [playersSorting, setPlayersSorting] = useState([
    {
      id: "time",
      desc: true,
    },
  ]);

  const [playersRowSelection, setPlayersRowSelection] = useState({});
  const [playersColumnFilters, setPlayersColumnFilters] = useState([]);
  const [playersTableConfig, setPlayersTableConfig] = useStorageState(
    localStorageConfig.LIVE_PLAYERS_TABLE_CONFIG.key,
    localStorageConfig.LIVE_PLAYERS_TABLE_CONFIG.defaultValue
  );

  const playersColumnVisibility = playersTableConfig.columnVisibility;

  const handlePlayersColumnVisibilityChange = (columnId, isVisible) => {
    setPlayersTableConfig((prev) => {
      const columnVisibility = { ...prev.columnVisibility };
      columnVisibility[columnId] === false ? delete columnVisibility[columnId] : columnVisibility[columnId] = isVisible;
      return { ...prev, columnVisibility }
    });
  };

  const playersTable = useReactTable({
    data: playersData,
    columns: playersColumns,
    onSortingChange: setPlayersSorting,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getCoreRowModel: getCoreRowModel(),
    onRowSelectionChange: setPlayersRowSelection,
    onColumnFiltersChange: setPlayersColumnFilters,
    onColumnVisibilityChange: handlePlayersColumnVisibilityChange,
    getRowId: (row) => row.player_id,
    state: {
      sorting: playersSorting,
      rowSelection: playersRowSelection,
      columnFilters: playersColumnFilters,
      columnVisibility: playersColumnVisibility,
    },
  });

  // ---------------- LOGS TABLE STATE -----------------
  const [logsFiltering, setLogsFiltering] = useState([]);
  const [logsTableConfig, setLogsTableConfig] = useStorageState(
    localStorageConfig.LIVE_LOGS_TABLE_CONFIG.key,
    localStorageConfig.LIVE_LOGS_TABLE_CONFIG.defaultValue
  );

  const logsColumnVisibility = logsTableConfig.columnVisibility;

  const [logsPagination, setLogsPagination] = useState({
    pageIndex: 0,
    pageSize: 100,
  });

  const handleLogsColumnVisibilityChange = (columnId, isVisible) => {
    setLogsTableConfig((prev) => {
      const columnVisibility = { ...prev.columnVisibility };
      columnVisibility[columnId] === false ? delete columnVisibility[columnId] : columnVisibility[columnId] = isVisible;
      return { ...prev, columnVisibility }
    });
  };

  const logsTable = useReactTable({
    data: logsView.logs,
    columns: logsColumns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onColumnFiltersChange: setLogsFiltering,
    onColumnVisibilityChange: handleLogsColumnVisibilityChange,
    onPaginationChange: setLogsPagination,
    autoResetPageIndex: false,
    state: {
      columnFilters: logsFiltering,
      columnVisibility: logsColumnVisibility,
      pagination: logsPagination,
    },
  });

  const selectedPlayers = useMemo(() => {
    return Object.keys(playersRowSelection)
      .map((key) => {
        return (
          playersTable.getSelectedRowModel().rows.find((row) => row.id === key)
            ?.original ?? null
        );
      })
      .filter(Boolean);
  }, [playersRowSelection, playersTable.getSelectedRowModel().rows]);

  return (
    <Grid container spacing={1}>
      <Grid size={12}>
        <Header data={gameData} />
      </Grid>
      <Grid
        size={{
          xs: 12,
          lg: "auto",
        }}
      >
        <PlayersTable
          table={playersTable}
          teamData={teamData}
          selectedPlayers={selectedPlayers}
          onColumnVisibilityChange={handlePlayersColumnVisibilityChange}
        />
      </Grid>
      <Grid
        size={{
          xs: 12,
          lg: "grow",
        }}
      >
        <LogsTable
          table={logsTable}
          logsViewData={logsView}
          searchParams={logsSearchParams}
          setSearchParams={setLogsSearchParams}
          onColumnVisibilityChange={handleLogsColumnVisibilityChange}
        />
      </Grid>
    </Grid>
  );
};

export default Live;
