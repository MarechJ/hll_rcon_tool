import { Fragment } from "react";
import { flexRender } from "@tanstack/react-table";
import { NoRowsOverlay } from "@/components/NoRowsOverlay";
import { StyledTable, StyledTd, StyledTh, StyledThead, StyledTr } from "./styles";
import { Box, LinearProgress } from "@mui/material";
import LoadingOverlay from "./LoadingOverlay";

const Table = ({ table, config = {}, renderSubComponent, rowProps = () => ({}), isLoading, isFetching }) => {
  return (
    <Box
      sx={{
        overflowX: "auto",
        overflowY: "hidden",
        width: "100%",
        scrollbarWidth: "thin",
        position: "relative",
        marginTop: "2px",
      }}
    >
      {isFetching && <LinearProgress sx={{ position: "absolute", top: 0, left: 0, width: "100%", height: "2px" }} />}
      <StyledTable density={config.density} fontSize={config.fontSize} data-expanded-view={String(config.expandedView)}>
        <StyledThead>
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
        </StyledThead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <Fragment key={row.id}>
              <StyledTr {...rowProps(row)}>
                {row.getVisibleCells().map((cell) => (
                  <StyledTd
                    key={cell.id}
                    variant={cell.column.columnDef?.meta?.variant}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </StyledTd>
                ))}
              </StyledTr>
              {row.getIsExpanded() && renderSubComponent && (
                <StyledTr>
                  {/* 2nd row is a custom 1 cell row */}
                  <StyledTd colSpan={row.getVisibleCells().length}>
                    {renderSubComponent({ row })}
                  </StyledTd>
                </StyledTr>
              )}
            </Fragment>
          ))}
        </tbody>
      </StyledTable>
      {isLoading && <LoadingOverlay />}
      {!isLoading && table.getRowModel().rows.length === 0 && <NoRowsOverlay />}
    </Box>
  );
};

export default Table;
