import { Stack } from "@mui/material";

export const TableToolbar = ({ children, ...props }) => (
  <Stack
    direction="row"
    sx={{
      borderRadius: 0,
      border: (theme) => `1px solid ${theme.palette.divider}`,
      borderBottom: "none",
    }}
    {...props}
  >
    {children}
  </Stack>
);
