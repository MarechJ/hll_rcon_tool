import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  FormControl,
  FormControlLabel,
  FormGroup,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid2";

const SYNC_METHODS = {
  ignore_unknown: "Ignore unknown VIPs",
  remove_unknown: "Remove unknown VIPs",
};

const SYNC_DESCRIPTIONS = {
  ignore_unknown:
    "VIPs which exist on the gameserver but not in this list are preserved.",
  remove_unknown:
    "During synchronization, VIPs not covered by a configured list may be removed from the gameserver.",
};

export default function VipListDialog({
  open,
  initialValues,
  title,
  submitLabel,
  loading,
  serverNumber,
  servers = {},
  allowDefaultSelection = false,
  onClose,
  onSubmit,
}) {
  const [name, setName] = useState("");
  const [sync, setSync] = useState("ignore_unknown");
  const [serverNumbers, setServerNumbers] = useState(null);
  const [serverError, setServerError] = useState("");
  const [setAsDefault, setSetAsDefault] = useState(false);

  useEffect(() => {
    if (!open) return;

    const servers = initialValues?.servers ?? null;

    setName(initialValues?.name ?? "");
    setSync(initialValues?.sync ?? "ignore_unknown");
    setServerNumbers(
      Array.isArray(servers)
        ? [...new Set(servers.map(Number))]
            .filter(Number.isInteger)
            .sort((left, right) => left - right)
        : null
    );
    setServerError("");
    setSetAsDefault(false);
  }, [initialValues, open]);

  const serverLabel = Number.isInteger(serverNumber)
    ? `server #${serverNumber}`
    : "the current server";

  const knownServerNumbers = Object.keys(servers)
    .map(Number)
    .filter(Number.isInteger)
    .sort((left, right) => left - right);

  const toggleAllServers = (enabled) => {
    if (enabled) {
      setServerNumbers(null);
    } else {
      const initialSelection =
        knownServerNumbers.length > 0
          ? knownServerNumbers
          : Number.isInteger(serverNumber)
          ? [serverNumber]
          : [];

      setServerNumbers(initialSelection);
    }

    setServerError("");
  };

  const toggleServer = (number, enabled) => {
    const selected = Array.isArray(serverNumbers) ? [...serverNumbers] : [];

    const next = enabled
      ? [...new Set([...selected, number])]
      : selected.filter((candidate) => candidate !== number);

    setServerNumbers(next.sort((left, right) => left - right));
    setServerError("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setServerError("");

    if (Array.isArray(serverNumbers) && serverNumbers.length === 0) {
      setServerError("Select at least one server.");
      return;
    }

    if (
      setAsDefault &&
      Number.isInteger(serverNumber) &&
      serverNumbers !== null &&
      !serverNumbers.includes(serverNumber)
    ) {
      setServerError(
        `Include server #${serverNumber} or apply the list to all servers before setting it as default.`
      );
      return;
    }

    try {
      await onSubmit({
        name: name.trim(),
        sync,
        servers: serverNumbers,
        setAsDefault,
      });
    } catch {
      // The mutation displays the API error and keeps the dialog open.
    }
  };

  return (
    <Dialog
      open={open}
      onClose={loading ? undefined : onClose}
      fullWidth
      maxWidth="sm"
      PaperProps={{ component: "form", onSubmit: handleSubmit }}
    >
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <Stack spacing={2.5} sx={{ pt: 1 }}>
          <DialogContentText>
            Changes are stored in the CRCON database. This operation does not
            synchronize a gameserver.
          </DialogContentText>

          <TextField
            required
            autoFocus
            label="List name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            disabled={loading}
            inputProps={{ maxLength: 255 }}
          />

          <FormControl required disabled={loading}>
            <InputLabel id="vip-list-sync-label">
              Synchronization mode
            </InputLabel>
            <Select
              labelId="vip-list-sync-label"
              label="Synchronization mode"
              value={sync}
              onChange={(event) => setSync(event.target.value)}
            >
              {Object.entries(SYNC_METHODS).map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Alert severity={sync === "remove_unknown" ? "warning" : "info"}>
            {SYNC_DESCRIPTIONS[sync]}
          </Alert>

          <Paper
            variant="outlined"
            sx={{ p: 2, bgcolor: "background.default" }}
          >
            <Stack spacing={1.5}>
              <Stack
                direction={{ xs: "column", sm: "row" }}
                alignItems={{ xs: "flex-start", sm: "center" }}
                justifyContent="space-between"
                gap={1}
              >
                <Typography variant="subtitle1" fontWeight={600}>
                  Servers
                </Typography>
                <FormControlLabel
                  label="Enable on all servers"
                  control={
                    <Switch
                      checked={serverNumbers === null}
                      onChange={(event) =>
                        toggleAllServers(event.target.checked)
                      }
                      disabled={loading}
                    />
                  }
                />
              </Stack>

              <Divider />

              {knownServerNumbers.length === 0 ? (
                <Alert severity="warning">
                  No CRCON servers are currently available for selection.
                </Alert>
              ) : (
                <FormGroup>
                  <Grid container spacing={0.5}>
                    {knownServerNumbers.map((number) => (
                      <Grid key={number} size={{ xs: 12, sm: 6 }}>
                        <FormControlLabel
                          label={servers[number]}
                          control={
                            <Checkbox
                              checked={
                                serverNumbers === null ||
                                serverNumbers.includes(number)
                              }
                              disabled={loading || serverNumbers === null}
                              onChange={(event) =>
                                toggleServer(number, event.target.checked)
                              }
                            />
                          }
                        />
                      </Grid>
                    ))}
                  </Grid>
                </FormGroup>
              )}

              {serverError && <Alert severity="error">{serverError}</Alert>}
            </Stack>
          </Paper>

          {allowDefaultSelection && (
            <>
              <FormControlLabel
                control={
                  <Switch
                    checked={setAsDefault}
                    onChange={(event) => setSetAsDefault(event.target.checked)}
                    disabled={loading}
                  />
                }
                label={`Set as default VIP list for ${serverLabel}`}
              />
              <Alert severity="info">
                New VIP records created from live-player and automated workflows
                can use this list after those integrations are enabled. Existing
                records and the gameserver are not changed.
              </Alert>
            </>
          )}
        </Stack>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          type="submit"
          variant="contained"
          disabled={loading || name.trim() === ""}
        >
          {submitLabel}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
