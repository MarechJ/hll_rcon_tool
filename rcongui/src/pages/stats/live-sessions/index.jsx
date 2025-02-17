import { Box, IconButton } from "@mui/material";
import { useMemo, useState } from "react";
import { teamsLiveQuery } from "@/queries/teams-live-query";
import {
  getExpandedRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { getCoreRowModel } from "@tanstack/react-table";
import { columns } from "./columns";
import Table from "@/components/table/Table";
import { isLeader, normalizePlayerProfile } from "@/utils/lib";
import { extractPlayers } from "@/utils/extractPlayers";
import { TableToolbar } from "@/components/table/TableToolbar";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import { generatePlayerActions } from "@/features/player-action/actions";
import { useLiveSessionsTableStore } from "@/stores/table-config";
import TableConfigDrawer from "@/components/table/TableConfigDrawer";
import SettingsIcon from "@mui/icons-material/Settings";

const LiveSessionsPage = () => {
  const { data } = teamsLiveQuery({ refetchInterval: 15 * 1000 });

  const tableConfig = useLiveSessionsTableStore();
  const [tableConfigDrawerOpen, setTableConfigDrawerOpen] = useState(false);
  const setConfig = useLiveSessionsTableStore(state => state.setConfig);

  const playersData = useMemo(() => {
    if (!data) return [];

    const players = extractPlayers(data).map((player) => ({
      ...player,
      profile: normalizePlayerProfile(player?.profile),
    }));

    const teams = players.reduce(
      (acc, player) => {
        let [teamName, unitName] = [player.team, player.unit_name];
        teamName =
          teamName !== "axis" && teamName !== "allies" ? "neutral" : teamName;
        if (!acc[teamName][unitName]) {
          acc[teamName][unitName] = {
            players: [],
            leader: null,
            unitName,
            teamName,
          };
        }
        acc[teamName][unitName].players.push(player);
        if (!acc[teamName][unitName].leader && isLeader(player.role)) {
          acc[teamName][unitName].leader = player;
        }
        return acc;
      },
      { axis: {}, allies: {}, neutral: {} }
    );

    const teamsRows = Object.values(teams).map((team) =>
      Object.values(team).map((unit) => {
        let unitData = {};
        if (unit.teamName !== "neutral") {
          unitData =
            unit.unitName !== "commmand"
              ? data[unit.teamName]["squads"][unit.unitName]
              : { type: "armycommander" };
        }

        const unitLeader = unit.leader ?? {
          profile: normalizePlayerProfile({}),
          name: unit.teamName === "neutral" ? "Unassigned" : "No Leader",
          unit_name: unit.unitName,
          team: unit.teamName,
          role: "",
          level: 0,
          time: 0,
        };

        return {
          ...unitLeader,
          ...unitData,
          subrows: unit.players,
        };
      })
    );

    return teamsRows.reduce((acc, team) => [...acc, ...team], []);
  }, [data]);

  const table = useReactTable({
    data: playersData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSubRows: (row) => row.subrows,
  });

  return (
    <Box>
      <TableToolbar table={table}>
        <ActionMenuButton
          actions={generatePlayerActions({
            multiAction: true,
            onlineAction: true,
          })}
          disabled={
            !table.getIsSomePageRowsSelected() && !table.getIsAllRowsSelected()
          }
          recipients={table.getSelectedRowModel().rows.map((row) => row.original)}
          orientation="horizontal"
          disableRipple={true}
          sx={{
            p: "1px 4px",
            height: "100%",
          }}
        />
        <DebouncedSearchInput
          placeholder={"Search player"}
          initialValue={table.getColumn("name")?.getFilterValue() ?? ""}
          onChange={(value) => {
            table.getColumn("name")?.setFilterValue(value);
          }}
          sx={{
            maxWidth: "300px",
          }}
        />
        <IconButton
          size="small"
          sx={{ p: 0.5, borderRadius: 0 }}
          onClick={() => setTableConfigDrawerOpen(true)}
        >
          <SettingsIcon sx={{ fontSize: "1rem" }} />
        </IconButton>
      </TableToolbar>
      <Table table={table} config={tableConfig} />
      <TableConfigDrawer
        name="Live Sessions"
        open={tableConfigDrawerOpen}
        onClose={(config) => {
          setTableConfigDrawerOpen(false);
          setConfig(config);
        }}
        config={tableConfig}
      />
    </Box>
  );
};

export default LiveSessionsPage;
