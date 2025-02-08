import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import Table from "@/components/table/Table";
import { TableToolbar } from "@/components/table/TableToolbar";
import { Box, Divider, IconButton } from "@mui/material";
import { useState } from "react";
import SettingsIcon from "@mui/icons-material/Settings";
import TableConfigDrawer from "@/components/table/TableConfigDrawer";
import NavPagination from "./nav-pagination";
import { useGameListTableStore } from "@/stores/table-config";

export function GameListTable({ table, maxPages, page }) {
  const [tableConfigDrawerOpen, setTableConfigDrawerOpen] = useState(false);
  const tableConfig = useGameListTableStore();
  const setConfig = useGameListTableStore(state => state.setConfig);

  const handleTableConfigClick = () => {
    // toggle config drawer
    setTableConfigDrawerOpen((prev) => !prev);
  };

  return (
    <Box>
      <TableToolbar>
        <DebouncedSearchInput
          placeholder={"Search games"}
          onChange={(value) => {
            // set global filter
            table.getColumn("map").setFilterValue(String(value));
          }}
          sx={{ maxWidth: 230 }}
        />
        <NavPagination page={page} maxPages={maxPages} />
        <Divider flexItem orientation="vertical" />
        <IconButton
          size="small"
          sx={{ width: 20, height: 20, borderRadius: 0, p: 2 }}
          onClick={handleTableConfigClick}
        >
          <SettingsIcon sx={{ fontSize: 16 }} />
        </IconButton>
      </TableToolbar>
      <Table table={table} config={tableConfig} />
      <TableConfigDrawer
        name="Games List"
        open={tableConfigDrawerOpen}
        onClose={(config) => {
          setTableConfigDrawerOpen(false);
          setConfig(config);
        }}
        config={tableConfig}
      />
    </Box>
  );
}
