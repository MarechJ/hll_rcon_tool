import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { Checkbox, FormControl, FormControlLabel, FormGroup, InputLabel, MenuItem, Select, Switch, Typography } from '@mui/material';
import Grid from "@mui/material/Grid2";
import { Fragment, useEffect, useState } from "react";

export const SYNC_METHODS = {
  ignore_unknown: "Ignore Unknown",
  remove_unknown: 'Remove Unknown',
}

const SYNC_METHOD_DESCRIPTIONS = {
  ignore_unknown: "Players with VIP on the game server but no records are ignored. Use this if you manage VIP records through an additional tool (Battlemetrics, etc.)",
  remove_unknown: "Players with VIP on the game server but no records have their VIP removed when lists are synched.",
}

export default function VipListCreateDialog({
  open,
  setOpen,
  servers,
  onSubmit,
  initialValues,
  titleText = "Edit VipList",
  submitText = "Save",
}) {
  const [name, setName] = useState("");
  const [serverNumbers, setServerNumbers] = useState(null);
  const [syncMethod, setSyncMethod] = useState("");

  useEffect(() => {
    if (initialValues) {
      if (initialValues.name !== undefined) setName(initialValues.name);
      if (initialValues.servers !== undefined) setServerNumbers(initialValues.servers);
      if (initialValues.syncMethod !== undefined) setSyncMethod(initialValues.syncMethod);
    }
  }, [open])

  const handleClose = () => {
    setOpen(false);
    setName("");
    setServerNumbers(null);
    setSyncMethod("");
  }

  function toggleAllServers(enabled) {
    setServerNumbers(enabled ? null : Object.keys(servers).map(n => parseInt(n)));
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
    (<Dialog
      open={open}
      onClose={handleClose}
      PaperProps={{
        component: 'form',
        onSubmit: (event) => {
          event.preventDefault();
          const data = {
            name,
            servers: serverNumbers,
            syncMethod,
          }
          onSubmit(data);
          handleClose();
        },
      }}
    >
      <DialogTitle>{titleText}</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Vip Lists are collections of records to provide both greater flexibility and
          portability than regular bans.
        </DialogContentText>

        <Grid container justifyContent="space-between" spacing={4}>
          <Grid size={6}>
            <TextField
              required
              id="name"
              name="name"
              label="Name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              fullWidth
              variant="standard"
            />
          </Grid>
          <Grid size={6}>
            <FormControl required fullWidth>
              <InputLabel>Sync Method</InputLabel>
              <Select
                label="Sync Method"
                value={syncMethod}
                onChange={(e) => setSyncMethod(e.target.value)}
              >
                {Object.entries(SYNC_METHODS).map(([value, name]) => (
                  <MenuItem key={value} value={value}>{name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
        <Typography variant="caption">
          {SYNC_METHOD_DESCRIPTIONS[syncMethod]}
        </Typography>
        <br />
        <Typography variant="h6">Servers</Typography>

        <Grid container alignContent="flex-start">
          <Grid size={6}>
            <FormGroup>
              {Object.entries(servers).map(([number, name]) => (
                <FormControlLabel key={number} label={name} control={
                  <Checkbox
                    checked={serverNumbers === null || serverNumbers.includes(parseInt(number))}
                    disabled={serverNumbers === null}
                    onChange={(e) => toggleServer(parseInt(number), e.target.checked)}
                  />
                } />
              ))}
            </FormGroup>
          </Grid>
          <Grid size={6}>
            <FormControlLabel
              label="Enable on all servers"
              control={
                <Switch
                  checked={serverNumbers === null}
                  onChange={(e) => toggleAllServers(e.target.checked)}
                />
              } />
          </Grid>
        </Grid>

      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button type="submit" disabled={name === "" || syncMethod === ""}>{submitText}</Button>
      </DialogActions>
    </Dialog>)
  );
}

export function VipListListCreateButton({
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
      <VipListCreateDialog
        open={open}
        setOpen={setOpen}
        servers={servers}
        onSubmit={onSubmit}
        initialValues={initialValues}
        titleText="Create Vip List"
        submitText="Create List"
      />
    </Fragment>
  )
}
