import Table from "@/components/table/Table";
import TableConfigDrawer from "@/components/table/TableConfigDrawer";
import storageKeys from "@/config/storageKeys";
import { Divider, IconButton, Stack } from "@mui/material";
import { useState } from "react";
import { useStorageState } from "@/hooks/useStorageState";
import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import SettingsIcon from "@mui/icons-material/Settings";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { playerProfileActions } from "@/features/player-action/actions";
import { TablePagination } from "@/components/table/TablePagination";
import { TableToolbar } from "@/components/table/TableToolbar";
import { Box, Typography } from "@mui/material";

const renderSubComponent = ({ row }) => {
  // Create a custom component that renders the player's stats
  const statCategories = {
    combat: [
      { label: "Kills", value: row.original.kills },
      { label: "Deaths", value: row.original.deaths },
      {
        label: "K/D",
        value: (row.original.kills / Math.max(row.original.deaths, 1)).toFixed(
          2
        ),
      },
      { label: "K/M", value: row.original.kills_per_minute?.toFixed(2) },
    ],
    teamwork: [
      { label: "Team Kills", value: row.original.teamkills },
      { label: "TK Streak", value: row.original.teamkills_streak },
      { label: "Deaths by TK", value: row.original.deaths_by_tk },
      { label: "TD Streak", value: row.original.deaths_by_tk_streak },
    ],
    offense: [
      { label: "Offensive Kills", value: row.original.offensive_kills },
      { label: "Defensive Kills", value: row.original.defensive_kills },
    ],
  };

  const StatSection = ({ title, stats }) => (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 1 }}>
        {title}
      </Typography>
      {stats.map(({ label, value }) => (
        <Box
          key={label}
          sx={{ display: "flex", justifyContent: "space-between", py: 0.5 }}
        >
          <Typography variant="body2">{label}:</Typography>
          <Typography variant="body2" sx={{ ml: 2 }}>
            {value}
          </Typography>
        </Box>
      ))}
    </Box>
  );

  const weapons = Object.entries(row.original.weapons || {}).map(
    ([weapon, kills]) => (
      <Box
        key={weapon}
        sx={{ display: "flex", justifyContent: "space-between", py: 0.5 }}
      >
        <Typography variant="body2">{weapon}:</Typography>
        <Typography variant="body2" sx={{ ml: 2 }}>
          {kills}
        </Typography>
      </Box>
    )
  );

  const deathsByWeapon = Object.entries(
    row.original.death_by_weapons || {}
  ).map(([weapon, deaths]) => (
    <Box
      key={weapon}
      sx={{ display: "flex", justifyContent: "space-between", py: 0.5 }}
    >
      <Typography variant="body2">{weapon}:</Typography>
      <Typography variant="body2" sx={{ ml: 2 }}>
        {deaths}
      </Typography>
    </Box>
  ));

  const deathsByPlayer = Object.entries(row.original.death_by || {}).map(
    ([player, deaths]) => (
      <Box
        key={player}
        sx={{ display: "flex", justifyContent: "space-between", py: 0.5 }}
      >
        <Typography variant="body2">{player}:</Typography>
        <Typography variant="body2" sx={{ ml: 2 }}>
          {deaths}
        </Typography>
      </Box>
    )
  );

  return (
    <Box sx={{ p: 2, maxWidth: { xs: (theme) => theme.breakpoints.values.sm, lg: "100%" } }}>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" },
          gap: { xs: 2, md: 4 },
          mb: 4,
        }}
      >
        <StatSection title="Combat Stats" stats={statCategories.combat} />
        <StatSection title="Teamwork Stats" stats={statCategories.teamwork} />
        <StatSection title="Objective Stats" stats={statCategories.offense} />
      </Box>

      <Box
        sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" }, gap: { xs: 2, md: 4 } }}
      >
        <Box>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Kills by Weapon
          </Typography>
          {weapons}
        </Box>
        <Box>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Deaths by Weapon
          </Typography>
          {deathsByWeapon}
        </Box>
        <Box>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Deaths by Player
          </Typography>
          {deathsByPlayer}
        </Box>
      </Box>
    </Box>
  );
};

const PlayersTable = ({ table, selectedPlayers }) => {
  const [tableConfigDrawerOpen, setTableConfigDrawerOpen] = useState(false);

  const [tableConfig, setTableConfig] = useStorageState(
    storageKeys.PLAYERS_TABLE_CONFIG,
    {
      density: "normal",
      fontSize: "normal",
    }
  );

  const handleTableConfigClick = () => {
    // toggle config drawer
    setTableConfigDrawerOpen((prev) => !prev);
  };

  return (
    <>
      <TableToolbar>
        <ActionMenuButton
          actions={playerProfileActions}
          disabled={
            !table.getIsSomePageRowsSelected() && !table.getIsAllRowsSelected()
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
          placeholder={"Search player"}
          initialValue={table.getColumn("name")?.getFilterValue() ?? ""}
          onChange={(value) => {
            table.getColumn("name")?.setFilterValue(value);
          }}
          sx={{ maxWidth: 230 }}
        />
        <TablePagination table={table} />
        <Divider flexItem orientation="vertical" />
        <IconButton
          size="small"
          sx={{ p: 0.5, borderRadius: 0 }}
          onClick={handleTableConfigClick}
        >
          <SettingsIcon sx={{ fontSize: 16 }} />
        </IconButton>
      </TableToolbar>
      <Table
        table={table}
        config={tableConfig}
        renderSubComponent={renderSubComponent}
      />
      <TableConfigDrawer
        name={"Players"}
        open={tableConfigDrawerOpen}
        onClose={(config) => {
          setTableConfigDrawerOpen(false);
          setTableConfig(config);
        }}
        config={tableConfig}
      />
    </>
  );
};

export default PlayersTable;
