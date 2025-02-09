import {
  Box,
  Divider,
  IconButton,
  Stack,
  Select,
  MenuItem,
} from "@mui/material";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft";
import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";

export const TablePagination = ({ table }) => (
  <Stack direction={"row"} gap={0.25} alignItems={"center"}>
    <IconButton
      onClick={() => table.firstPage()}
      disabled={!table.getCanPreviousPage()}
      size="small"
      sx={{ borderRadius: 0, p: 0.5 }}
    >
      <KeyboardDoubleArrowLeftIcon />
    </IconButton>
    <IconButton
      onClick={() => table.previousPage()}
      disabled={!table.getCanPreviousPage()}
      size="small"
      sx={{ borderRadius: 0, p: 0.5 }}
    >
      <KeyboardArrowLeftIcon />
    </IconButton>
    <Box sx={{ textWrap: "nowrap", alignSelf: "center", mx: 0.5 }}>
      {table.getState().pagination.pageIndex + 1} of{" "}
      {table.getPageCount().toLocaleString()}
    </Box>
    <IconButton
      onClick={() => table.nextPage()}
      disabled={!table.getCanNextPage()}
      size="small"
      sx={{ borderRadius: 0, p: 0.5 }}
    >
      <KeyboardArrowRightIcon />
    </IconButton>
    <IconButton
      onClick={() => table.lastPage()}
      disabled={!table.getCanNextPage()}
      size="small"
      sx={{ borderRadius: 0, p: 0.5 }}
    >
      <KeyboardDoubleArrowRightIcon />
    </IconButton>
    <Divider orientation="vertical" flexItem />
    <Box sx={{ mx: 0.25 }}>
      <Select
        value={table.getState().pagination.pageSize}
        onChange={(e) => table.setPageSize(e.target.value)}
        size="small"
        sx={{ borderRadius: 0 }}
        aria-label="Page size"
      >
        {[50, 100, 150, 250, 500].map((pageSize) => (
          <MenuItem key={pageSize} value={pageSize}>
            Show {pageSize}
          </MenuItem>
        ))}
      </Select>
    </Box>
  </Stack>
);
