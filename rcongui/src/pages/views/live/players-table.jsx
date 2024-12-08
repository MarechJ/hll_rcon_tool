import Table from "@/components/table/Table";
import TableConfigDrawer from "@/components/table/TableConfigDrawer";
import storageKeys from "@/config/storageKeys";
import { IconButton, Stack } from "@mui/material";
import { useState } from "react";
import { useStorageState } from "@/hooks/useStorageState";
import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import SettingsIcon from "@mui/icons-material/Settings"
import { TeamSelectionToolbar } from "./TeamSelectionToolbar";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { generatePlayerActions } from "@/features/player-action/actions";

const PlayersTable = ({ table, teamData, selectedPlayers }) => {

  const [tableConfigDrawerOpen, setTableConfigDrawerOpen] =
  useState(false);

  const [tableConfig, setTableConfig] = useStorageState(
    storageKeys.LIVE_PLAYERS_TABLE_CONFIG,
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
      <TeamSelectionToolbar table={table} teamData={teamData} />
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
            actions={generatePlayerActions({
              multiAction: true,
              onlineAction: true,
            })}
            disabled={
              !table.getIsSomePageRowsSelected() &&
              !table.getIsAllRowsSelected()
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
            initialValue={
              table.getColumn("name")?.getFilterValue() ?? ""
            }
            onChange={(value) => {
              table.getColumn("name")?.setFilterValue(value);
            }}
          />
          <IconButton
            size="small"
            sx={{ p: 0.5, borderRadius: 0 }}
            onClick={handleTableConfigClick}
          >
            <SettingsIcon sx={{ fontSize: 16 }} />
          </IconButton>
        </Stack>
        <Table table={table} config={tableConfig} />
      </Stack>
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
  )
};

export default PlayersTable;
