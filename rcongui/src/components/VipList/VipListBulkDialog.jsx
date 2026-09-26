import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { DesktopDateTimePicker } from "@mui/x-date-pickers/DesktopDateTimePicker";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import dayjs from "dayjs";

const ACTION_LABELS = {
  activate: "Activate records",
  deactivate: "Deactivate records",
  expiration: "Set expiration",
  never: "Remove expiration",
  description: "Replace manual player name",
  notes: "Replace notes",
  move: "Move to another list",
  export_csv: "Export as CSV",
  export_json: "Export as JSON",
  delete: "Delete permanently",
};

export default function VipListBulkDialog({
  open,
  vipList,
  vipLists,
  records,
  canChange,
  canDelete,
  loading,
  onClose,
  onSubmit,
}) {
  const [step, setStep] = useState("configure");
  const [action, setAction] = useState("deactivate");
  const [textValue, setTextValue] = useState("");
  const [targetListId, setTargetListId] = useState("");
  const [expiresAt, setExpiresAt] = useState(() => dayjs().add(1, "month"));

  useEffect(() => {
    if (!open) return;

    setStep("configure");
    setAction(
      canChange
        ? "deactivate"
        : canDelete
        ? "delete"
        : "export_csv"
    );
    setTextValue("");
    setTargetListId("");
    setExpiresAt(dayjs().add(1, "month"));
  }, [canChange, canDelete, open]);

  const safeRecords = Array.isArray(records) ? records : [];
  const availableTargetLists = (vipLists ?? []).filter(
    (item) => item.id !== vipList?.id
  );
  const canEditDescriptions = safeRecords.every(
    (record) => !record.player_name
  );
  const recordIds = useMemo(
    () => safeRecords.map((record) => record.id),
    [safeRecords]
  );

  const expirationInvalid =
    action === "expiration" &&
    (!expiresAt || !expiresAt.isValid());
  const targetListInvalid =
    action === "move" && !Number.isInteger(targetListId);

  const buildOperation = () => {
    const operation = {
      kind:
        action === "delete"
          ? "delete"
          : action.startsWith("export_")
          ? "export"
          : "edit",
      action,
      recordIds,
    };

    if (action === "activate") operation.active = true;
    if (action === "deactivate") operation.active = false;
    if (action === "expiration") operation.expiresAt = expiresAt;
    if (action === "never") operation.expiresAt = null;
    if (action === "description") operation.description = textValue.trim();
    if (action === "notes") operation.notes = textValue.trim();
    if (action === "move") operation.vipListId = targetListId;
    if (action === "export_csv") operation.format = "csv";
    if (action === "export_json") operation.format = "json";

    return operation;
  };

  const operationSummary = () => {
    if (action === "activate") return "Status will be set to active.";
    if (action === "deactivate") return "Status will be set to inactive.";
    if (action === "expiration") {
      return `Expiration will be set to ${expiresAt.format(
        "YYYY-MM-DD HH:mm"
      )}.`;
    }
    if (action === "never") return "Expiration will be removed.";
    if (action === "description") {
      return textValue.trim()
        ? `Description will be replaced with “${textValue.trim()}”.`
        : "Description will be cleared.";
    }
    if (action === "notes") {
      return textValue.trim()
        ? `Notes will be replaced with “${textValue.trim()}”.`
        : "Notes will be cleared.";
    }
    if (action === "move") {
      const target = availableTargetLists.find(
        (item) => item.id === targetListId
      );
      return `Records will be moved to “${target?.name ?? "Unknown list"}”.`;
    }
    if (action === "export_csv") {
      return "Selected records will be downloaded as a portable CSV file.";
    }
    if (action === "export_json") {
      return "Selected records will be downloaded as a structured JSON file.";
    }
    return "The selected records will be permanently deleted.";
  };

  const handleConfirm = async () => {
    try {
      await onSubmit(buildOperation());
    } catch {
      // The mutation displays the error and keeps the review open.
    }
  };

  return (
    <Dialog
      open={open}
      onClose={loading ? undefined : onClose}
      fullWidth
      maxWidth="md"
    >
      <DialogTitle>
        {step === "configure"
          ? "Configure bulk operation"
          : "Review bulk operation"}
      </DialogTitle>

      <DialogContent>
        {step === "configure" ? (
          <Stack spacing={2.5} sx={{ pt: 1 }}>
            <DialogContentText>
              Configure an operation for {safeRecords.length} selected VIP
              records in “{vipList?.name}”.
            </DialogContentText>

            <FormControl fullWidth>
              <InputLabel id="vip-bulk-action-label">Action</InputLabel>
              <Select
                labelId="vip-bulk-action-label"
                label="Action"
                value={action}
                onChange={(event) => setAction(event.target.value)}
                disabled={loading}
              >
                {canChange && (
                  <MenuItem value="activate">Activate records</MenuItem>
                )}
                {canChange && (
                  <MenuItem value="deactivate">Deactivate records</MenuItem>
                )}
                {canChange && (
                  <MenuItem value="expiration">Set expiration</MenuItem>
                )}
                {canChange && (
                  <MenuItem value="never">Remove expiration</MenuItem>
                )}
                {canChange && canEditDescriptions && (
                  <MenuItem value="description">
                    Replace manual player name
                  </MenuItem>
                )}
                {canChange && availableTargetLists.length > 0 && (
                  <MenuItem value="move">
                    Move to another list
                  </MenuItem>
                )}
                <MenuItem value="export_csv">Export as CSV</MenuItem>
                <MenuItem value="export_json">Export as JSON</MenuItem>
                {canChange && (
                  <MenuItem value="notes">Replace notes</MenuItem>
                )}
                {canDelete && (
                  <MenuItem value="delete">Delete permanently</MenuItem>
                )}
              </Select>
            </FormControl>

            {action === "move" && (
              <FormControl fullWidth error={targetListInvalid}>
                <InputLabel id="vip-target-list-label">
                  Target VIP list
                </InputLabel>
                <Select
                  labelId="vip-target-list-label"
                  label="Target VIP list"
                  value={targetListId}
                  onChange={(event) =>
                    setTargetListId(Number(event.target.value))
                  }
                  disabled={loading}
                >
                  {availableTargetLists.map((item) => (
                    <MenuItem key={item.id} value={item.id}>
                      {item.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}

            {action === "expiration" && (
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DesktopDateTimePicker
                  label="New expiration"
                  value={expiresAt}
                  onChange={setExpiresAt}
                  format="LLL"
                  ampm={false}
                  disabled={loading}
                  maxDate={dayjs("2999-12-31T23:59:59+00:00")}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      error: expirationInvalid,
                      helperText: expirationInvalid
                        ? "Enter a valid expiration."
                        : "The same expiration is applied to every selected record.",
                    },
                  }}
                />
              </LocalizationProvider>
            )}

            {(action === "description" || action === "notes") && (
              <TextField
                autoFocus
                label={
                  action === "description"
                    ? "New description"
                    : "New notes"
                }
                value={textValue}
                onChange={(event) => setTextValue(event.target.value)}
                multiline={action === "notes"}
                minRows={action === "notes" ? 3 : undefined}
                helperText="An empty value clears this field on every selected record."
                disabled={loading}
              />
            )}

            {action === "delete" && (
              <Alert severity="error">
                Deletion is permanent and cannot be undone.
              </Alert>
            )}

            <Alert severity="info">
              No gameserver synchronization is performed by this operation.
            </Alert>
          </Stack>
        ) : (
          <Stack spacing={2.5} sx={{ pt: 1 }}>
            <Alert severity={action === "delete" ? "error" : "warning"}>
              Review the complete operation before confirming it.
            </Alert>

            <Paper variant="outlined" sx={{ p: 2 }}>
              <Stack spacing={1}>
                <Typography>
                  <strong>VIP list:</strong> {vipList?.name}
                </Typography>
                <Typography>
                  <strong>Selected records:</strong> {safeRecords.length}
                </Typography>
                <Typography>
                  <strong>Action:</strong> {ACTION_LABELS[action]}
                </Typography>
                <Typography>{operationSummary()}</Typography>
              </Stack>
            </Paper>

            <Paper variant="outlined">
              <Typography variant="subtitle2" sx={{ px: 2, pt: 1.5 }}>
                Affected records
              </Typography>
              <List dense sx={{ maxHeight: 260, overflow: "auto" }}>
                {safeRecords.map((record) => (
                  <ListItem key={record.id} divider>
                    <ListItemText
                      primary={
                        record.description ||
                        `VIP record #${record.id}`
                      }
                      secondary={`${record.player_id} · Record #${record.id}`}
                      secondaryTypographyProps={{
                        sx: {
                          fontFamily: "monospace",
                          overflowWrap: "anywhere",
                        },
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>

            <Alert severity="info">
              No gameserver synchronization is performed. The operation is
              executed atomically: if one record is invalid, none are changed.
            </Alert>
          </Stack>
        )}
      </DialogContent>

      <DialogActions>
        {step === "review" && (
          <Button
            onClick={() => setStep("configure")}
            disabled={loading}
          >
            Back
          </Button>
        )}
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        {step === "configure" ? (
          <Button
            variant="contained"
            onClick={() => setStep("review")}
            disabled={
              loading ||
              safeRecords.length === 0 ||
              expirationInvalid ||
              targetListInvalid
            }
          >
            Review changes
          </Button>
        ) : (
          <Button
            color={action === "delete" ? "error" : "primary"}
            variant="contained"
            onClick={handleConfirm}
            disabled={loading}
          >
            {action === "delete"
              ? "Confirm permanent deletion"
              : "Confirm and apply"}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
