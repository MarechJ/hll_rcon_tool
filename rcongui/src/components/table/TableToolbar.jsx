import { Stack } from "@mui/material";

export const TableToolbar = ({ children, ...props }) => (
  <Stack
    direction="row"
    flexWrap={"wrap"}
    alignItems={"center"}
    sx={{
    borderBottom: "none",
      borderRadius: 0,
      borderWidth: "1px",
      borderStyle: "solid",
      borderColor: (theme) => theme.palette.divider,
      ...(props?.sx ?? {}),
    }}
  >
    {children}
  </Stack>
);