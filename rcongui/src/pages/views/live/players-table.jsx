import React from "react";
import { flexRender } from "@tanstack/react-table";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import { NoRowsOverlay } from "@/components/NoRowsOverlay";
import { StyledTable, StyledTd, StyledTh, StyledTr } from "./styled-table";

const PlayersTable = ({ table, size }) => {
  const { switchPlayer } = usePlayerSidebar();

  return (
    <>
      <StyledTable size={size}>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <StyledTr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <StyledTh key={header.id}>
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
              onClick={() => switchPlayer(row.original.player_id)}
            >
              {row.getVisibleCells().map((cell) => (
                <StyledTd key={cell.id}>
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
    </>
  );
};

export default PlayersTable;
