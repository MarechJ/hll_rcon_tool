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

export default function BlacklistRecordCreateDialog({
  open,
  setOpen,
  blacklists,
  onSubmit,
  initialValues,
  disablePlayerId,
}) {
  const [blacklist, setBlacklist] = React.useState("");
  const [playerId, setPlayerId] = React.useState("");
  const [expiresAt, setExpiresAt] = React.useState("");
  const [reason, setReason] = React.useState("");

  React.useEffect(() => {
    if (initialValues) {
      if (initialValues.blacklistId !== undefined) {
        const blacklist = blacklists.find((b) => b.id === initialValues.blacklistId);
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
      <DialogTitle>Blacklist Player</DialogTitle>
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
            { blacklists.map(
              (b) => <MenuItem key={b.id} value={b}>{b.name}</MenuItem>
            ) }
          </Select>
        </FormControl>

        { blacklist ? (
          <React.Fragment>
            { blacklist.servers !== null && !blacklist.servers.includes(process.env.SERVER_NUMBER) ? (
              <Typography variant="caption" color="secondary">
                { blacklist.servers.size > 0
                  ? `This blacklist only affects server ${blacklist.servers.join(", ").replace()}!`
                  : `This blacklist does not affect any servers!` }
              </Typography>
            ) : "" }

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
                  <MenuItem value={60*60}>1 hour</MenuItem>
                  <MenuItem value={60*60*6}>6 hours</MenuItem>
                  <MenuItem value={60*60*12}>12 hours</MenuItem>
                  <MenuItem value={60*60*24}>1 day</MenuItem>
                  <MenuItem value={60*60*24*2}>2 days</MenuItem>
                  <MenuItem value={60*60*24*3}>3 days</MenuItem>
                  <MenuItem value={60*60*24*5}>5 days</MenuItem>
                  <MenuItem value={60*60*24*7}>7 days</MenuItem>
                  <MenuItem value={60*60*24*14}>14 days</MenuItem>
                  <MenuItem value={60*60*24*30}>30 days</MenuItem>
                  <MenuItem value={60*60*24*365}>365 days</MenuItem>
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
        ) : "" }

        
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button type="submit" disabled={blacklist === ""}>Blacklist Player</Button>
      </DialogActions>
    </Dialog>
  );
}

export function BlacklistRecordCreateButton({
  blacklists,
  onSubmit,
  initialValues,
  disablePlayerId,
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
        Create New Record
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
