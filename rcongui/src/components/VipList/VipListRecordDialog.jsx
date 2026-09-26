import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControlLabel,
  Paper,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import { DesktopDateTimePicker } from "@mui/x-date-pickers/DesktopDateTimePicker";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import dayjs from "dayjs";
import { TimePickerButtons } from "@/components/shared/TimePickerButtons";

const PRESET_TIMES = [
  [2, "hours"],
  [1, "day"],
  [1, "week"],
  [1, "month"],
];

const isSupportedPlayerId = (value) =>
  /^\d{17}$/.test(value) || /^[0-9a-fA-F]{32}$/.test(value);

export default function VipListRecordDialog({
  open,
  mode,
  initialValues,
  vipList,
  loading,
  onClose,
  onSubmit,
}) {
  const editing = mode === "edit";
  const hasKnownPlayerName = Boolean(
    editing && initialValues?.playerName
  );
  const [playerId, setPlayerId] = useState("");
  const [description, setDescription] = useState("");
  const [notes, setNotes] = useState("");
  const [active, setActive] = useState(true);
  const [expiresAt, setExpiresAt] = useState(null);
  const [playerIdError, setPlayerIdError] = useState("");

  useEffect(() => {
    if (!open) return;

    setPlayerId(initialValues?.playerId ?? "");
    setDescription(initialValues?.description ?? "");
    setNotes(initialValues?.notes ?? "");
    setActive(initialValues?.active ?? true);
    setExpiresAt(
      initialValues?.expiresAt
        ? dayjs(initialValues.expiresAt)
        : null
    );
    setPlayerIdError("");
  }, [initialValues, open]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const normalizedPlayerId = playerId.trim();

    if (!editing && !isSupportedPlayerId(normalizedPlayerId)) {
      setPlayerIdError(
        "Enter a 17-digit Steam64 ID or a 32-character hexadecimal EOS ID."
      );
      return;
    }

    try {
      await onSubmit({
        playerId: normalizedPlayerId,
        vipListId: vipList.id,
        description: description.trim(),
        notes: notes.trim(),
        active,
        expiresAt,
      });
    } catch {
      // The mutation displays the error and keeps the dialog open.
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
      <DialogTitle>
        {editing ? "Edit VIP record" : "Add VIP record"}
      </DialogTitle>

      <DialogContent>
        <Stack spacing={2.5} sx={{ pt: 1 }}>
          <DialogContentText>
            This record will be stored in “{vipList?.name}”. No gameserver
            synchronization is performed by this operation.
          </DialogContentText>

          <TextField
            required
            autoFocus={!editing}
            label="Steam64 or HLLV EOS ID"
            value={playerId}
            onChange={(event) => {
              setPlayerId(event.target.value);
              setPlayerIdError("");
            }}
            disabled={editing || loading}
            error={Boolean(playerIdError)}
            helperText={
              playerIdError ||
              (editing
                ? "The player ID of an existing record cannot be changed."
                : "Steam64: 17 digits · HLLV EOS: 32 hexadecimal characters")
            }
            inputProps={{ maxLength: 32 }}
          />

          <TextField
            label="Manual player name"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            disabled={loading || hasKnownPlayerName}
            helperText={
              hasKnownPlayerName
                ? `The player database name “${initialValues.playerName}” is used.`
                : "Only used when no player name exists in the player database."
            }
          />

          <TextField
            label="Notes"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            disabled={loading}
            multiline
            minRows={2}
          />

          <FormControlLabel
            control={
              <Switch
                checked={active}
                onChange={(event) => setActive(event.target.checked)}
                disabled={loading}
              />
            }
            label="Record is active"
          />

          <Paper
            variant="outlined"
            sx={{ p: 2, bgcolor: "background.default" }}
          >
            <Stack spacing={1.5}>
              <Typography variant="subtitle1" fontWeight={600}>
                Expiration
              </Typography>

              {expiresAt === null ? (
                <Alert severity="info">
                  This VIP record never expires.
                </Alert>
              ) : (
                <LocalizationProvider dateAdapter={AdapterDayjs}>
                  <DesktopDateTimePicker
                    label="Expiration"
                    value={expiresAt}
                    onChange={setExpiresAt}
                    format="LLL"
                    ampm={false}
                    disabled={loading}
                    maxDate={dayjs("2999-12-31T23:59:59+00:00")}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        helperText:
                          "Expired records remain available in the inactive section.",
                      },
                    }}
                  />
                </LocalizationProvider>
              )}

              <Stack
                direction={{ xs: "column", sm: "row" }}
                spacing={1}
                useFlexGap
                flexWrap="wrap"
              >
                {PRESET_TIMES.map(([amount, unit]) => (
                  <TimePickerButtons
                    key={`${amount}-${unit}`}
                    amount={amount}
                    unit={unit}
                    expirationTimestamp={expiresAt ?? dayjs()}
                    setExpirationTimestamp={setExpiresAt}
                  />
                ))}
              </Stack>

              <Button
                variant="outlined"
                color="secondary"
                onClick={() => setExpiresAt(null)}
                disabled={loading}
              >
                Never expires
              </Button>
            </Stack>
          </Paper>
        </Stack>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          type="submit"
          variant="contained"
          disabled={loading || (!editing && playerId.trim() === "")}
        >
          {editing ? "Save" : "Add record"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
