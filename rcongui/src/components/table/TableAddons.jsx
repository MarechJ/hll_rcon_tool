import { Box, ButtonGroup, Stack } from "@mui/material";

const TableAddons = ({ children }) => {
  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center">
        <ButtonGroup
          sx={{ ml: 0, "& .MuiButton-root": { borderRadius: "0 !important" } }}
          variant="outlined"
          size="small"
        >
          {children}
        </ButtonGroup>
      </Stack>
    </Box>
  );
};

export default TableAddons;
