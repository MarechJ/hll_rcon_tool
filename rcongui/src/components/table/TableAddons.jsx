import { Box, ButtonGroup, Stack } from "@mui/material";

const TableAddons = ({ children }) => {
  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center">
        <ButtonGroup
          style={{ marginLeft: 0 }}
          sx={{
            "& .MuiButton-root": {
              borderRadius: 0,
            },
          }}
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