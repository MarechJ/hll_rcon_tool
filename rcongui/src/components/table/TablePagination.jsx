import { IconButton, Stack } from "@mui/material";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft";
import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";

export const TablePagination = ({ table }) => (
  <Stack
    direction={"row"}
    justifyContent={"end"}
    alignItems={"center"}
    gap={0.25}
  >
    <IconButton
      onClick={() => table.firstPage()}
      disabled={!table.getCanPreviousPage()}
      size="small"
      sx={{ width: 20, height: 20, borderRadius: 0, p: 2 }}
    >
      <KeyboardDoubleArrowLeftIcon />
    </IconButton>
    <IconButton
      onClick={() => table.previousPage()}
      disabled={!table.getCanPreviousPage()}
      size="small"
      sx={{ width: 20, height: 20, borderRadius: 0, p: 2 }}
    >
      <KeyboardArrowLeftIcon />
    </IconButton>
    <span>
      <strong>
        {table.getState().pagination.pageIndex + 1} of{" "}
        {table.getPageCount().toLocaleString()}
      </strong>
    </span>
    <IconButton
      onClick={() => table.nextPage()}
      disabled={!table.getCanNextPage()}
      size="small"
      sx={{ width: 20, height: 20, borderRadius: 0, p: 2 }}
    >
      <KeyboardArrowRightIcon />
    </IconButton>
    <IconButton
      onClick={() => table.lastPage()}
      disabled={!table.getCanNextPage()}
      size="small"
      sx={{ width: 20, height: 20, borderRadius: 0, p: 2 }}
    >
      <KeyboardDoubleArrowRightIcon />
    </IconButton>
  </Stack>
);
