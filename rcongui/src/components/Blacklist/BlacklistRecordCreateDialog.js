import * as React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import { FormControl, Grid, InputLabel, MenuItem, Select, Typography } from '@material-ui/core';
import moment from "moment";
import { getServerStatus } from '../../utils/fetchUtils';

export default function BlacklistRecordCreateDialog({
  open,
  setOpen,
  blacklists,
  onSubmit,
  initialValues,
  titleText = "Blacklist Player",
  submitText = "Blacklist Player",
  disablePlayerId,
  hasManyIDs = false,
}) {
  const [blacklist, setBlacklist] = React.useState("");
  const [playerId, setPlayerId] = React.useState("");
  const [expiresAt, setExpiresAt] = React.useState("");
  const [reason, setReason] = React.useState("");
  const [currentServer, setCurrentServer] = React.useState({})

  React.useEffect(() => {
    getServerStatus().then(server => setCurrentServer(server)).catch(() => setCurrentServer({}))
  }, [])

  React.useEffect(() => {
    if (initialValues) {
      if (initialValues.blacklistId !== undefined) {
        const blacklist = blacklists?.find((b) => b.id === initialValues.blacklistId);
        if (blacklist) setBlacklist(blacklist);
      };
      if (initialValues.playerId !== undefined) setPlayerId(initialValues.playerId);
      if (initialValues.expiresAt !== undefined) {
        setExpiresAt(
          initialValues.expiresAt === null
            ? ""
            : initialValues.expiresAt
        );
      }
      if (initialValues.reason !== undefined) setReason(initialValues.reason);
    }
  }, [open])

  const handleClose = () => {
    setOpen(false);
    setBlacklist("")
    setPlayerId("")
    setExpiresAt("")
    setReason("")
  };

  const displayBlacklistWarning = () => {
    const affectsAllServers = blacklist.servers === null

    if (affectsAllServers) {
      return null;
    }

    let text = "";
    const affectsNone = blacklist.servers.length === 0;
    const failedToLoadCurrentServer = !("server_number" in currentServer);
    const affectsOnlyOtherServers = blacklist.servers.length > 0 && !blacklist.servers.includes(currentServer?.server_number ?? -1)

    if (affectsNone)
    {
      text = "This blacklist does not affect any servers!"
    } 
    else if (failedToLoadCurrentServer)
    {
      text = `Failed to load current server information!\n`
      text += `This blacklist MAY NOT affect THIS server. Affected servers: [${blacklist.servers.join(", ")}]`
    }
    else if (affectsOnlyOtherServers) 
    {
      text = `This blacklist DOES NOT affect THIS server! Affected servers: [${blacklist.servers.join(", ")}]`
    }

    return (
      <Typography variant="caption" color="secondary">
        {text}
      </Typography>
    )
  }

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      PaperProps={{
        component: 'form',
        onSubmit: (event) => {
          event.preventDefault();
          const data = {
            blacklistId: blacklist.id,
            playerId,
            expiresAt: expiresAt === "" ? null : expiresAt,
            reason
          }
          onSubmit(data);
          handleClose();
        },
      }}
    >
      <DialogTitle>{titleText}</DialogTitle>
      <DialogContent>
        <DialogContentText>
          By blacklisting a player you are revoking their access to one or more servers.
        </DialogContentText>

        <FormControl required fullWidth>
          <InputLabel>Blacklist</InputLabel>
          <Select
            value={blacklist}
            onChange={(e) => setBlacklist(e.target.value)}
          >
            {blacklists?.map(
              (b) => <MenuItem key={b.id} value={b}>{b.name}</MenuItem>
            )}
          </Select>
        </FormControl>

        {blacklist && (
          <React.Fragment>
            {displayBlacklistWarning()}
            <TextField
              required
              margin="dense"
              id="playerId"
              name="playerId"
              label="Player ID"
              type="text"
              value={playerId}
              onChange={(e) => setPlayerId(e.target.value)}
              fullWidth
              disabled={disablePlayerId}
              variant="standard"
              multiline={hasManyIDs}
            />

            <Grid container
              spacing={5}
              alignItems="center"
            >
              <Grid item xs={8}>
                <TextField
                  margin="dense"
                  id="expiresAt"
                  name="expiresAt"
                  label="Expires At (empty for never)"
                  InputLabelProps={{
                    shrink: true,
                  }}
                  type="datetime-local"
                  value={expiresAt}
                  onChange={(e) => setExpiresAt(e.target.value)}
                  fullWidth
                  variant="standard"
                />
              </Grid>
              <Grid item xs={4}>
                <InputLabel>Preset Times</InputLabel>
                <Select
                  placeholder="Preset Times"
                  value={""}
                  onChange={(e) => {
                    e.target.value
                      ? setExpiresAt(moment().utc().add(e.target.value, 'seconds').format("YYYY-MM-DDTHH:mm"))
                      : setExpiresAt("");
                  }}
                  fullWidth
                >
                  <MenuItem value={60 * 60}>1 hour</MenuItem>
                  <MenuItem value={60 * 60 * 6}>6 hours</MenuItem>
                  <MenuItem value={60 * 60 * 12}>12 hours</MenuItem>
                  <MenuItem value={60 * 60 * 24}>1 day</MenuItem>
                  <MenuItem value={60 * 60 * 24 * 2}>2 days</MenuItem>
                  <MenuItem value={60 * 60 * 24 * 3}>3 days</MenuItem>
                  <MenuItem value={60 * 60 * 24 * 5}>5 days</MenuItem>
                  <MenuItem value={60 * 60 * 24 * 7}>7 days</MenuItem>
                  <MenuItem value={60 * 60 * 24 * 14}>14 days</MenuItem>
                  <MenuItem value={60 * 60 * 24 * 30}>30 days</MenuItem>
                  <MenuItem value={60 * 60 * 24 * 365}>365 days</MenuItem>
                  <MenuItem value={null}>Never</MenuItem>
                </Select>
              </Grid>
            </Grid>
            <TextField
              required
              multiline
              margin="dense"
              id="reason"
              name="reason"
              label="Reason"
              type="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              fullWidth
              variant="standard"
              helperText="Available variables:
              {player_id}, {player_name}, {banned_at}, {banned_until}, {expires_at},
              {duration}, {expires}, {ban_id}, {blacklist_name}"
            />
          </React.Fragment>
        )}


      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button type="submit" disabled={blacklist === ""}>{submitText}</Button>
      </DialogActions>
    </Dialog>
  );
}

export function BlacklistRecordCreateButton({
  blacklists,
  onSubmit,
  initialValues,
  disablePlayerId,
  children,
}) {
  const [open, setOpen] = React.useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  return (
    <React.Fragment>
      <Button
        variant="contained"
        color="primary"
        size="large"
        onClick={handleClickOpen}
      >
        {children}
      </Button>
      <BlacklistRecordCreateDialog
        open={open}
        setOpen={setOpen}
        blacklists={blacklists}
        onSubmit={onSubmit}
        initialValues={initialValues}
        disablePlayerId={disablePlayerId}
      />
    </React.Fragment>
  )
}
