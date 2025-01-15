import Table from "@/components/table/Table";
import TableConfigDrawer from "@/components/table/TableConfigDrawer";
import localStorageConfig from "@/config/localStorage";
import { Divider, IconButton, Stack } from "@mui/material";
import { memo, useState } from "react";
import { useStorageState } from "@/hooks/useStorageState";
import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import SettingsIcon from "@mui/icons-material/Settings";
import UnfoldMoreIcon from "@mui/icons-material/UnfoldMore";
import UnfoldLessIcon from "@mui/icons-material/UnfoldLess";
import { TeamSelectionToolbar } from "./TeamSelectionToolbar";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { generatePlayerActions } from "@/features/player-action/actions";
import TableColumnSelection from "@/components/table/TableColumnSelection";
import { TableToolbar } from "@/components/table/TableToolbar";

const PlayersTable = ({ table, teamData, selectedPlayers, onColumnVisibilityChange }) => {
  console.log("RENDERING PLAYERS TABLE");

  const [tableConfigDrawerOpen, setTableConfigDrawerOpen] = useState(false);

  const [tableConfig, setTableConfig] = useStorageState(
    localStorageConfig.LIVE_PLAYERS_TABLE_CONFIG.key,
    localStorageConfig.LIVE_PLAYERS_TABLE_CONFIG.defaultValue
  );

  const handleTableConfigClick = () => {
    // toggle config drawer
    setTableConfigDrawerOpen((prev) => !prev);
  };

  return (
    <>
      <TeamSelectionToolbar table={table} teamData={teamData} />
      <Stack direction="column" spacing={0}>
        <TableToolbar>
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
            initialValue={table.getColumn("name")?.getFilterValue() ?? ""}
            onChange={(value) => {
              table.getColumn("name")?.setFilterValue(value);
            }}
          />
          <Divider flexItem orientation="vertical" sx={{ marginLeft: 0, marginRight: 0 }} />
          <IconButton
            size="small"
            aria-label={tableConfig.expandedView ? "Collapse" : "Expand"}
            aria-description={
              tableConfig.expandedView
                ? "Hide extra details"
                : "Show extra details"
            }
            sx={{ p: 0.5, borderRadius: 0 }}
            onClick={() => {
              setTableConfig((prev) => ({
                ...prev,
                expandedView: !prev.expandedView,
              }));
            }}
          >
            {tableConfig.expandedView ? (
              <UnfoldLessIcon sx={{ fontSize: "1rem" }} />
            ) : (
              <UnfoldMoreIcon sx={{ fontSize: "1rem" }} />
            )}
          </IconButton>
          <TableColumnSelection table={table} onColumnVisibilityChange={onColumnVisibilityChange} />
          <IconButton
            size="small"
            aria-label="Table settings"
            aria-description="Configure the table"
            sx={{ p: 0.5, borderRadius: 0 }}
            onClick={handleTableConfigClick}
          >
            <SettingsIcon sx={{ fontSize: "1rem" }} />
          </IconButton>
        </TableToolbar>
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
  );
};

export default memo(PlayersTable);
