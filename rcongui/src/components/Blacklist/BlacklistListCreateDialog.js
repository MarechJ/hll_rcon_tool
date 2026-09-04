import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import {
  Alert,
  Checkbox,
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
  Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import { Fragment, useEffect, useState } from "react";

export const SYNC_METHODS = {
  kick_only: "Kick Only",
  ban_on_connect: "Ban On Connect",
  ban_immediately: "Ban Immediately",
};

const SYNC_METHOD_DESCRIPTIONS = {
  kick_only:
    "Players are kicked every time they join. They can see the reason but have to wait in queue.",
  ban_on_connect:
    "Players can see the blacklist reason once. After that, they get banned.",
  ban_immediately:
    "Players will only see the blacklist reason if they are online when blacklisted.",
};

export default function BlacklistListCreateDialog({
  open,
  setOpen,
  servers,
  onSubmit,
  initialValues,
  titleText = "Edit Blacklist",
  submitText = "Save",
}) {
  const [name, setName] = useState("");
  const [serverNumbers, setServerNumbers] = useState(null);
  const [syncMethod, setSyncMethod] = useState("");

  useEffect(() => {
    if (initialValues) {
      if (initialValues.name !== undefined) setName(initialValues.name);
      if (initialValues.servers !== undefined)
        setServerNumbers(initialValues.servers);
      if (initialValues.syncMethod !== undefined)
        setSyncMethod(initialValues.syncMethod);
    }
  }, [open]);

  const handleClose = () => {
    setOpen(false);
    setName("");
    setServerNumbers(null);
    setSyncMethod("");
  };

  function toggleAllServers(enabled) {
    setServerNumbers(
      enabled ? null : Object.keys(servers).map((n) => parseInt(n))
    );
  }

  function toggleServer(number, enabled) {
    const nums = [...serverNumbers];

    if (enabled) {
      if (!nums.includes(number)) nums.push(number);
    } else {
      const index = nums.indexOf(number);
      if (index > -1) {
        nums.splice(index, 1);
      }
    }
    setServerNumbers(nums);
  }

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      fullWidth
      maxWidth="sm"
      PaperProps={{
        component: "form",
        onSubmit: (event) => {
          event.preventDefault();
          const data = {
            name,
            servers: serverNumbers,
            syncMethod,
          };
          onSubmit(data);
          handleClose();
        },
      }}
    >
      <DialogTitle sx={{ px: 3, pt: 3, pb: 1 }}>{titleText}</DialogTitle>
      <DialogContent sx={{ px: 3, py: 2 }}>
        <Stack spacing={2.5}>
          <DialogContentText>
            Blacklists are collections of ban-like records that provide greater
            flexibility and scalability than regular bans.
          </DialogContentText>

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                required
                id="name"
                name="name"
                label="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                fullWidth
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl required fullWidth>
                <InputLabel id="blacklist-sync-method-label">
                  Sync method
                </InputLabel>
                <Select
                  labelId="blacklist-sync-method-label"
                  label="Sync method"
                  value={syncMethod}
                  onChange={(e) => setSyncMethod(e.target.value)}
                >
                  {Object.entries(SYNC_METHODS).map(([value, label]) => (
                    <MenuItem key={value} value={value}>
                      {label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {syncMethod && (
            <Alert severity="info">
              {SYNC_METHOD_DESCRIPTIONS[syncMethod]}
            </Alert>
          )}

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
                      onChange={(e) => toggleAllServers(e.target.checked)}
                    />
                  }
                />
              </Stack>
              <Divider />
              <FormGroup>
                <Grid container spacing={0.5}>
                  {Object.entries(servers).map(([number, serverName]) => (
                    <Grid key={number} size={{ xs: 12, sm: 6 }}>
                      <FormControlLabel
                        label={serverName}
                        control={
                          <Checkbox
                            checked={
                              serverNumbers === null ||
                              serverNumbers.includes(parseInt(number))
                            }
                            disabled={serverNumbers === null}
                            onChange={(e) =>
                              toggleServer(parseInt(number), e.target.checked)
                            }
                          />
                        }
                      />
                    </Grid>
                  ))}
                </Grid>
              </FormGroup>
            </Stack>
          </Paper>
        </Stack>
      </DialogContent>
      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          variant="contained"
          type="submit"
          disabled={name === "" || syncMethod === ""}
        >
          {submitText}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export function BlacklistListCreateButton({
  servers,
  onSubmit,
  initialValues,
}) {
  const [open, setOpen] = useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  return (
    <Fragment>
      <Button
        variant="contained"
        color="primary"
        size="large"
        onClick={handleClickOpen}
      >
        Create New List
      </Button>
      <BlacklistListCreateDialog
        open={open}
        setOpen={setOpen}
        servers={servers}
        onSubmit={onSubmit}
        initialValues={initialValues}
        titleText="Create Blacklist"
        submitText="Create List"
      />
    </Fragment>
  );
}
