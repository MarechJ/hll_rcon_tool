import React from "react";
import { flexRender } from "@tanstack/react-table";
import { NoRowsOverlay } from "@/components/NoRowsOverlay";
import { StyledTable, StyledTd, StyledTh, StyledTr } from "./styles";
import { Box } from "@mui/material";

const Table = ({ table, config = {} }) => {
  return (
    <Box
      sx={{
        overflowX: "auto",
        overflowY: "hidden",
        width: "100%",
        scrollbarWidth: "thin",
      }}
    >
      <StyledTable density={config.density} fontSize={config.fontSize}>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <StyledTr key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <StyledTh
                    key={header.id}
                    variant={header.column.columnDef?.meta?.variant}
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
                );
              })}
            </StyledTr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <StyledTr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <StyledTd
                  key={cell.id}
                  variant={cell.column.columnDef?.meta?.variant}
                >
                  {cell.getIsGrouped() ? (
                    // If it's a grouped cell, add an expander and row count
                    <>
                      <button
                        {...{
                          onClick: row.getToggleExpandedHandler(),
                          style: {
                            cursor: row.getCanExpand() ? "pointer" : "normal",
                          },
                        }}
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </button>
                    </>
                  ) : cell.getIsAggregated() ? (
                    // If the cell is aggregated, use the Aggregated
                    // renderer for cell
                    flexRender(
                      cell.column.columnDef.aggregatedCell ??
                        cell.column.columnDef.cell,
                      cell.getContext()
                    )
                  ) : (
                    flexRender(cell.column.columnDef.cell, cell.getContext())
                  )}
                </StyledTd>
              ))}
            </StyledTr>
          ))}
        </tbody>
      </StyledTable>
      {table.getRowModel().rows.length === 0 && <NoRowsOverlay />}
    </Box>
  );
};

export default Table;
