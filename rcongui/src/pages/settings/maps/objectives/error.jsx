import { useRouteError, NavLink } from "react-router-dom";
import { Stack, Typography, Button, Paper } from "@mui/material";

export default function RouteError() {
  const error = useRouteError();
  // The backend throws a HTTP 400 (bad request) if the game mode doesn't support
  // selecting the objectives
  const isUnsupportedMode =
    error.message === "unsupported_mode" ||
    (error?.data?.command === "get_objective_rows" && error?.status === 400);
  // other error let handle higher error handler
  if (!isUnsupportedMode) throw error;
  return (
    <Stack
      id="error-page"
      spacing={2}
      alignItems={"center"}
      justifyContent={"center"}
      sx={{
        textAlign: "center",
        margin: "10rem auto",
        width: (theme) => theme.breakpoints.values.sm,
      }}
    >
      <Typography variant="h1">Unsupported mode</Typography>
      <Typography variant="h2">
        Changing objectives is not supported in this game mode.
      </Typography>
      <Button
        variant="contained"
        LinkComponent={NavLink}
        to={"/settings/maps/change"}
      >
        Change map
      </Button>
    </Stack>
  );
}
