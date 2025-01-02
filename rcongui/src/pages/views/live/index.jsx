import {useMemo, useState} from "react";
import {cmd} from "@/utils/fetchUtils";
import {columns as playersColumns} from "./players-columns";
import {Header} from "@/components/game/Header";
import {extractPlayers, extractTeamState} from "@/utils/extractPlayers";
import {useLoaderData} from "react-router-dom";
import {useQuery} from "@tanstack/react-query";
import PlayersTable from "./players-table";
import LogsTable from "./logs-table";
import {logsColumns} from "./logs-columns";
import {useStorageState} from "@/hooks/useStorageState";
import {teamsLiveQueryOptions} from "@/queries/teams-live-query";
import {normalizePlayerProfile} from "@/utils/lib";
import {
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable
} from "@tanstack/react-table";
import Grid from "@mui/material/Grid2";
import storageKeys from "@/config/storageKeys";

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

  return {initialLogsView: response};
};

const Live = () => {
  // ---------------- VIEW STATE -----------------
  const {initialLogsView} = useLoaderData();

  // ---------------- PLAYERS DATA -----------------
  const {data: teamData} = useQuery({
    ...teamsLiveQueryOptions,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

  // const teamData = teamViewResponse.result;

  const playersData = useMemo(() => {
    if (!teamData) return [];
    return extractPlayers(teamData).map((player) => ({
      ...player,
      profile: normalizePlayerProfile(player?.profile),
    }));
  }, [teamData]);

  // ---------------- LOGS DATA -----------------
  // Using custom hook that synchronizes the components state
  // and the browser's local storage
  const [logsSearchParams, setLogsSearchParams] = useStorageState(
    storageKeys.LIVE_LOGS_SEARCH_PARAMS,
    {
      players: [],
      actions: [],
      inclusive: true,
      limit: 500,
    }
  );

  const {data: logsView} = useQuery({
    queryKey: [
      "logs",
      "live",
      {
        end: logsSearchParams.limit,
        filter_action: logsSearchParams.actions,
        filter_player: logsSearchParams.players,
        inclusive_filter: logsSearchParams.inclusive,
      },
    ],
    queryFn: () =>
      cmd.GET_LIVE_LOGS({
        payload: {
          end: logsSearchParams.limit,
          filter_action: logsSearchParams.actions,
          filter_player: logsSearchParams.players,
          inclusive_filter: logsSearchParams.inclusive,
        },
      }),
    select: (response) => response.result,
    initialData: initialLogsView,
    refetchInterval: interval, // Polling interval for updates
  });

  // ---------------- GAME HEADER DATA -----------------
  const {data: gameState} = useQuery({
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
  const [playersSorting, setPlayersSorting] = useState([{
    id: "time",
    desc: true,
  }]);
  const [playersRowSelection, setPlayersRowSelection] = useState({});
  const [playersColumnFilters, setPlayersColumnFilters] = useState([]);

  const playersTable = useReactTable({
    data: playersData,
    columns: playersColumns,
    onSortingChange: setPlayersSorting,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getCoreRowModel: getCoreRowModel(),
    onRowSelectionChange: setPlayersRowSelection,
    onColumnFiltersChange: setPlayersColumnFilters,
    getRowId: (row) => row.player_id,
    state: {
      sorting: playersSorting,
      rowSelection: playersRowSelection,
      columnFilters: playersColumnFilters,
    },
  });

  // ---------------- LOGS TABLE STATE -----------------
  const [logsFiltering, setLogsFiltering] = useState([]);

  const logsTable = useReactTable({
    data: logsView.logs,
    columns: logsColumns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onColumnFiltersChange: setLogsFiltering,
    initialState: {
      pagination: {
        pageIndex: 0,
        pageSize: 100,
      },
    },
    state: {
      columnFilters: logsFiltering,
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
        <Header data={gameData}/>
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
        />
      </Grid>
    </Grid>
  );
};

export default Live;
