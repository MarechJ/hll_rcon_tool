import { Alert, Chip, Stack, Typography } from "@mui/material";

const triggerLabels = {
  startup: "Handler startup",
  notification: "VIP List change",
  periodic: "Periodic safety sync",
  manual: "Manual synchronization",
};

const formatTimestamp = (value) => {
  if (!value) return "Never";

  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) return value;

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(timestamp);
};

const VipSyncStatus = ({ status, error }) => {
  if (error) {
    return (
      <Alert severity="error">
        The synchronization status could not be loaded.
      </Alert>
    );
  }

  if (!status || status.state === "never") {
    return (
      <Alert severity="info">
        No completed VIP synchronization has been recorded yet.
      </Alert>
    );
  }

  const severity =
    status.state === "running"
      ? "info"
      : status.state === "successful"
      ? "success"
      : "error";

  const stateLabel =
    status.state === "running"
      ? "Synchronization running"
      : status.state === "successful"
      ? "Last synchronization successful"
      : "Last synchronization failed";

  return (
    <Stack spacing={1.5}>
      <Alert severity={severity}>
        <Stack spacing={0.5}>
          <Typography variant="subtitle2">{stateLabel}</Typography>
          <Typography variant="body2">
            Trigger:{" "}
            {triggerLabels[status.trigger] ?? status.trigger ?? "Unknown"}
          </Typography>
          <Typography variant="body2">
            Started: {formatTimestamp(status.started_at)}
          </Typography>
          <Typography variant="body2">
            Completed: {formatTimestamp(status.completed_at)}
          </Typography>
          <Typography variant="body2">
            Last successful sync: {formatTimestamp(status.last_success_at)}
          </Typography>
        </Stack>
      </Alert>

      <Stack direction="row" gap={1} flexWrap="wrap">
        <Chip
          size="small"
          color="success"
          variant="outlined"
          label={`${status.added ?? 0} added or updated`}
        />
        <Chip
          size="small"
          color="error"
          variant="outlined"
          label={`${status.removed ?? 0} removed`}
        />
        <Chip
          size="small"
          color={status.failures?.length ? "error" : "default"}
          variant="outlined"
          label={`${status.failures?.length ?? 0} failures`}
        />
      </Stack>

      {status.failures?.map((failure, index) => (
        <Alert
          key={`${failure.action}-${failure.player_id ?? "general"}-${index}`}
          severity="error"
        >
          {failure.action?.toUpperCase()}
          {failure.player_id ? ` ${failure.player_id}` : ""}: {failure.error}
        </Alert>
      ))}
    </Stack>
  );
};

export default VipSyncStatus;
