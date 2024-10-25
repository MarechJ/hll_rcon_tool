import {
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  useReactTable,
  flexRender,
} from "@tanstack/react-table";
import { useState } from "react";
import { StyledTable, StyledTd, StyledTh, StyledTr } from "./styled-table";

// Implementation of Tanstack React Table v8 using basic HTML table elements
export default function LogsTable({ data, columns, size }) {
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
    state: {
      sorting,
      filtering,
      pagination,
    },
  });

  return (
    <div>
      <div>
        <StyledTable size={size}>
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <StyledTr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <StyledTh
                    key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
                    size={header.column.columnDef.meta?.size}
                  >
                    {header.isPlaceholder ? null : (
                      <div>
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                      </div>
                    )}
                  </StyledTh>
                ))}
              </StyledTr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <StyledTr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <StyledTd key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </StyledTd>
                ))}
              </StyledTr>
            ))}
          </tbody>
        </StyledTable>
        {table.getRowModel().rows.length === 0 && <NoRowsOverlay />}
      </div>
      {/* TODO: Replace tailwind className with MUI sx prop */}
      <div sx={{ height: "8px" }} />
      <div sx={{ display: "flex", justifyContent: "center", flexGap: 2 }}>
        <button
          className="border rounded p-1"
          sx={{ border: "1px solid", borderRadius: "4px", padding: "4px" }}
          onClick={() => table.firstPage()}
          disabled={!table.getCanPreviousPage()}
        >
          {"<<"}
        </button>
        <button
          className="border rounded p-1"
          sx={{ border: "1px solid", borderRadius: "4px", padding: "4px" }}
          onClick={() => table.previousPage()}
          disabled={!table.getCanPreviousPage()}
        >
          {"<"}
        </button>
        <button
          className="border rounded p-1"
          sx={{ border: "1px solid", borderRadius: "4px", padding: "4px" }}
          onClick={() => table.nextPage()}
          disabled={!table.getCanNextPage()}
        >
          {">"}
        </button>
        <button
          className="border rounded p-1"
          sx={{ border: "1px solid", borderRadius: "4px", padding: "4px" }}
          onClick={() => table.lastPage()}
          disabled={!table.getCanNextPage()}
        >
          {">>"}
        </button>
        <span sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <div>Page</div>
          <strong>
            {table.getState().pagination.pageIndex + 1} of{" "}
            {table.getPageCount().toLocaleString()}
          </strong>
        </span>
        <span sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          | Go to page:
          <input
            type="number"
            min="1"
            max={table.getPageCount()}
            defaultValue={table.getState().pagination.pageIndex + 1}
            onChange={(e) => {
              const page = e.target.value ? Number(e.target.value) - 1 : 0;
              table.setPageIndex(page);
            }}
            sx={{
              border: "1px solid",
              borderRadius: "4px",
              padding: "4px",
              width: "16ch",
            }}
          />
        </span>
        <select
          value={table.getState().pagination.pageSize}
          onChange={(e) => {
            table.setPageSize(Number(e.target.value));
          }}
        >
          {[10, 20, 30, 40, 50].map((pageSize) => (
            <option key={pageSize} value={pageSize}>
              Show {pageSize}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
