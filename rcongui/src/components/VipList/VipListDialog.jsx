import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Switch,
  TextField,
} from "@mui/material";

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

function parseServerNumbers(value) {
  const tokens = value.trim().split(/[\s,;]+/).filter(Boolean);

  if (tokens.length === 0) {
    throw new Error("Enter at least one server number.");
  }

  const numbers = tokens.map(Number);

  if (
    numbers.some(
      (number) =>
        !Number.isInteger(number) || number < 1 || number > 32
    )
  ) {
    throw new Error(
      "Server numbers must be whole numbers between 1 and 32."
    );
  }

  return [...new Set(numbers)].sort((left, right) => left - right);
}

export default function VipListDialog({
  open,
  initialValues,
  title,
  submitLabel,
  loading,
  serverNumber,
  allowDefaultSelection = false,
  onClose,
  onSubmit,
}) {
  const [name, setName] = useState("");
  const [sync, setSync] = useState("ignore_unknown");
  const [allServers, setAllServers] = useState(true);
  const [serverNumbers, setServerNumbers] = useState("");
  const [serverError, setServerError] = useState("");
  const [setAsDefault, setSetAsDefault] = useState(false);

  useEffect(() => {
    if (!open) return;

    const servers = initialValues?.servers ?? null;

    setName(initialValues?.name ?? "");
    setSync(initialValues?.sync ?? "ignore_unknown");
    setAllServers(servers === null);
    setServerNumbers(
      Array.isArray(servers) ? servers.join(", ") : ""
    );
    setServerError("");
    setSetAsDefault(false);
  }, [initialValues, open]);

  const serverLabel = Number.isInteger(serverNumber)
    ? `server #${serverNumber}`
    : "the current server";

  const handleSubmit = async (event) => {
    event.preventDefault();
    setServerError("");

    let servers = null;

    if (!allServers) {
      try {
        servers = parseServerNumbers(serverNumbers);
      } catch (error) {
        setServerError(error.message);
        return;
      }
    }

    if (
      setAsDefault &&
      Number.isInteger(serverNumber) &&
      servers !== null &&
      !servers.includes(serverNumber)
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
        servers,
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

          <Alert
            severity={sync === "remove_unknown" ? "warning" : "info"}
          >
            {SYNC_DESCRIPTIONS[sync]}
          </Alert>

          <FormControlLabel
            control={
              <Switch
                checked={allServers}
                onChange={(event) => {
                  setAllServers(event.target.checked);
                  setServerError("");
                }}
                disabled={loading}
              />
            }
            label="Apply to all CRCON servers"
          />

          {!allServers && (
            <TextField
              required
              label="Server numbers"
              value={serverNumbers}
              onChange={(event) => {
                setServerNumbers(event.target.value);
                setServerError("");
              }}
              error={Boolean(serverError)}
              helperText={
                serverError ||
                "Comma-separated CRCON server numbers, for example: 1, 2, 4"
              }
              disabled={loading}
            />
          )}

          {allowDefaultSelection && (
            <>
              <FormControlLabel
                control={
                  <Switch
                    checked={setAsDefault}
                    onChange={(event) =>
                      setSetAsDefault(event.target.checked)
                    }
                    disabled={loading}
                  />
                }
                label={`Set as default VIP list for ${serverLabel}`}
              />
              <Alert severity="info">
                New VIP records created from live-player and automated
                workflows can use this list after those integrations are
                enabled. Existing records and the gameserver are not changed.
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
