import { isRouteErrorResponse } from "react-router-dom";
import { useRouteError, useLocation } from "react-router-dom";
import { Stack, Typography, Button, Paper } from "@mui/material";
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faDiscord } from "@fortawesome/free-brands-svg-icons";
import siteConfig from "@/config/siteConfig";

export default function RouteError() {
  const error = useRouteError();
  const location = useLocation();
  console.error(error);
  if (
    isRouteErrorResponse(error) &&
    error.status >= 400 &&
    error.status < 500
  ) {
    // the response json is automatically parsed to
    // `error.data`, you also have access to the status
    return (
      <Stack spacing={2} alignItems={"center"} justifyContent={"center"}>
        <Typography variant="h3">{error.status}</Typography>
        <Typography variant="h4">
          {error.data.text ?? error.data.message ?? error.statusText}
        </Typography>
        <Typography>{error.data.command ?? error.data}</Typography>
        <Typography>{error.data.name ?? error.data.error}</Typography>
        <Button variant="contained" LinkComponent={Link} to={location.pathname}>
          Try again!
        </Button>
      </Stack>
    );
  }

  return (
    <Stack
      id="error-page"
      spacing={2}
      alignItems={"center"}
      justifyContent={"center"}
      sx={{ textAlign: "center" }}
    >
      <Typography variant="h1">Oops!</Typography>
      <Typography variant="h2">
        Sorry, an unexpected error has occurred.
      </Typography>
      <Typography variant="h3">
        Please contact support when this error persists.
      </Typography>
      <Paper elevation={4} variant="outlined" sx={{ padding: 2 }}>
        <Typography variant="h4">Error: {error.name ?? "Unknown"}</Typography>
        <Typography variant="body1">
          <i>{error.statusText || error.message || error.data}</i>
        </Typography>
      </Paper>
      <Stack direction={"row"} spacing={2}>
        <Button
          variant="contained"
          color="error"
          LinkComponent={"a"}
          href={siteConfig.bugReportChannelUrl}
          startIcon={<FontAwesomeIcon icon={faDiscord} />}
        >
          Report this error
        </Button>
        <Button variant="contained" LinkComponent={Link} to={location.pathname}>
          Go back
        </Button>
      </Stack>
    </Stack>
  );
}
