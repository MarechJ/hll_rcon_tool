import React, { useState } from "react";
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import { NoRowsOverlay } from "@/components/NoRowsOverlay";
import { StyledTable, StyledTd, StyledTh, StyledTr } from "./styled-table";
import { Box } from "@mui/material";

const PlayersTable = ({ data, columns, size }) => {
  const { openWithId, switchPlayer } = usePlayerSidebar();

  const [sorting, setSorting] = useState([]);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    getCoreRowModel: getCoreRowModel(),
    state: {
      sorting,
    },
  });

  return (
    <Box sx={{ overflowX: "auto", overflowY: "hidden", width: "100%", scrollbarWidth: "none" }}>
      <div>
        <StyledTable size={size}>
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <StyledTr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <StyledTh
                    key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
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
              <StyledTr
                key={row.id}
                onDoubleClick={() => openWithId(row.original.player_id)}
                onClick={() => switchPlayer(row.original.player_id)}
              >
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
    </Box>
  );
};

export default PlayersTable;
