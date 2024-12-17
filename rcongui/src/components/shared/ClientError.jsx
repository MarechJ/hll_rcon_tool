import { Alert, AlertTitle, Typography } from "@mui/material";

/**
 * Display an error message to the user
 * @param {Error} error
 */
export function ClientError({ error }) {
  return (
    <Alert severity="error">
      <AlertTitle>{error.name ?? "Error"}</AlertTitle>
      <Typography variant="body2">
        {error.command && `Command: ${error.command}`}
      </Typography>
      <Typography variant="body2">
        {error?.text ??  error?.message ?? "An error occured with your request. Open up your browser's console to investigate."}
      </Typography>
    </Alert>
  );
}
