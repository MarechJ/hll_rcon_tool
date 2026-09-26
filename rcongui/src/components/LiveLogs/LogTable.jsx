import {
  Box,
  Button,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useState } from "react";

export default function LogTable({ data, columns }) {
  const [sorting, setSorting] = useState([]);
  const [filtering, setFiltering] = useState([]);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 100,
  });

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: setPagination,
    onSortingChange: setSorting,
    onColumnFiltersChange: setFiltering,
    state: { sorting, filtering, pagination },
  });

  return (
    <Stack gap={1}>
      <TableContainer
        sx={(theme) => ({
          overflowX: "auto",
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: 0,
        })}
      >
        <Table size="small" sx={{ tableLayout: "fixed" }}>
          <TableHead>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableCell
                    key={header.id}
                    sx={{
                      width: header.column.getSize(),
                      bgcolor: "background.paper",
                    }}
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id} hover>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell
                      key={cell.id}
                      sx={{ width: cell.column.getSize() }}
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} align="center">
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Stack
        direction={{ xs: "column", md: "row" }}
        alignItems={{ xs: "stretch", md: "center" }}
        justifyContent="center"
        gap={1}
      >
        <Stack direction="row" gap={0.5}>
          <Button
            size="small"
            variant="outlined"
            onClick={() => table.firstPage()}
            disabled={!table.getCanPreviousPage()}
          >
            First
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={() => table.lastPage()}
            disabled={!table.getCanNextPage()}
          >
            Last
          </Button>
        </Stack>

        <Typography variant="body2" sx={{ whiteSpace: "nowrap" }}>
          Page <strong>{table.getState().pagination.pageIndex + 1}</strong> of{" "}
          {table.getPageCount().toLocaleString()}
        </Typography>

        <TextField
          type="number"
          label="Go to page"
          value={table.getState().pagination.pageIndex + 1}
          onChange={(event) => {
            const page = event.target.value
              ? Number(event.target.value) - 1
              : 0;
            table.setPageIndex(page);
          }}
          slotProps={{
            htmlInput: { min: 1, max: Math.max(1, table.getPageCount()) },
          }}
          sx={{ width: 120 }}
        />

        <Box>
          <Select
            value={table.getState().pagination.pageSize}
            onChange={(event) => table.setPageSize(Number(event.target.value))}
            aria-label="Rows per page"
          >
            {[10, 20, 30, 40, 50, 100].map((pageSize) => (
              <MenuItem key={pageSize} value={pageSize}>
                Show {pageSize}
              </MenuItem>
            ))}
          </Select>
        </Box>
      </Stack>
    </Stack>
  );
}
