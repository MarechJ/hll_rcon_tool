import Table from "@/components/table/Table";
import {
  Stack,
  Typography,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Divider,
} from "@mui/material";
import { memo, useState } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
} from "@tanstack/react-table";
import { TableToolbar } from "@/components/table/TableToolbar";
import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import { TablePagination } from "@/components/table/TablePagination";
import SplitButton from "@/components/shared/SplitButton";

const VipTable = memo(
  ({
    data,
    columns,
    isLoading,
    isFetching,
    handleBulkRemove,
    editSelected,
  }) => {
    const [pagination, setPagination] = useState({
      pageIndex: 0,
      pageSize: 50,
    });
    const [globalFilter, setGlobalFilter] = useState("");
    const [columnVisibility, setColumnVisibility] = useState({
      player_id: false,
    });
    const [columnFilters, setColumnFilters] = useState([]);

    const table = useReactTable({
      data: data || [],
      columns,
      getCoreRowModel: getCoreRowModel(),
      getPaginationRowModel: getPaginationRowModel(),
      getSortedRowModel: getSortedRowModel(),
      getFilteredRowModel: getFilteredRowModel(),
      onPaginationChange: setPagination,
      onGlobalFilterChange: setGlobalFilter,
      onColumnVisibilityChange: setColumnVisibility,
      onFiltersChange: setColumnFilters,
      globalFilterFn: "includesString",
      state: {
        pagination,
        globalFilter,
        columnVisibility,
        filters: columnFilters,
      },
    });

    const rowsCount = table.getRowCount();
    const selectedRows = table.getSelectedRowModel().rows.length;

    return (
      <Stack
        component="section"
        sx={{ width: "100%", bgcolor: "background.paper" }}
      >
        <Stack
          direction="row"
          alignItems="center"
          spacing={1}
          sx={{ width: "100%", p: 1 }}
        >
          <Button
            disabled={selectedRows === 0 || isFetching}
            variant="contained"
            color="primary"
            size="small"
            onClick={() => editSelected(table)}
          >
            Edit Selected
          </Button>
          <Button
            disabled={selectedRows === 0 || isFetching}
            variant="contained"
            color="error"
            size="small"
            onClick={() => handleBulkRemove(table)}
          >
            Remove Selected
          </Button>
        </Stack>
        <TableToolbar>
          <Stack
            direction="row"
            alignItems="center"
            spacing={1}
            sx={{ width: "100%", p: 1 }}
          >
            <DebouncedSearchInput
              placeholder={"Search player"}
              onChange={(value) => {
                setGlobalFilter(value);
              }}
            />
            <StatusFilter
              value={
                table
                  .getState()
                  .columnFilters.find((filter) => filter.id === "status")?.value
              }
              onChange={(value) => {
                table.setColumnFilters([{ id: "status", value }]);
              }}
            />
          </Stack>
          <Divider orientation="horizontal" flexItem sx={{ width: "100%" }} />
          <Stack
            direction="row"
            alignItems="center"
            flexWrap="wrap"
            spacing={2}
            sx={{ width: "100%", p: 1 }}
          >
            <Typography variant="body2">
              {selectedRows} / {rowsCount} selected
            </Typography>
            <TablePagination table={table} />
          </Stack>
        </TableToolbar>
        <Table table={table} isLoading={isLoading} isFetching={isFetching} />
      </Stack>
    );
  }
);

export const StatusFilter = ({ value, onChange }) => {
  return (
    <FormControl sx={{ minWidth: 120 }} size="small">
      <InputLabel id="status-filter-label">Status</InputLabel>
      <Select
        labelId="status-filter-label"
        id="status-filter"
        value={value}
        label="Status"
        onChange={(event) => onChange(event.target.value)}
      >
        <MenuItem value="">
          <em>All</em>
        </MenuItem>
        <MenuItem value="active">Active</MenuItem>
        <MenuItem value="expired">Expired</MenuItem>
      </Select>
    </FormControl>
  );
};

export default VipTable;
