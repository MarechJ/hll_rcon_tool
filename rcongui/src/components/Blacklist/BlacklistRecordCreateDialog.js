import * as React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import { FormControl, Grid, InputLabel, makeStyles, MenuItem, Select, Typography } from '@material-ui/core';
import moment from "moment";
import { getServerStatus, getSharedMessages } from '../../utils/fetchUtils';
import TextHistory from '../textHistory';

const ONE_HOUR = 60 * 60;
const ONE_DAY = ONE_HOUR * 24;
const presetTimes = [
  { label: "1 hour", value: ONE_HOUR },
  { label: "6 hours", value: ONE_HOUR * 6 },
  { label: "12 hours", value: ONE_HOUR * 12 },
  { label: "1 day", value: ONE_DAY },
  { label: "2 days", value: ONE_DAY * 2 },
  { label: "3 days", value: ONE_DAY * 3 },
  { label: "5 days", value: ONE_DAY * 5 },
  { label: "7 days", value: ONE_DAY * 7 },
  { label: "14 days", value: ONE_DAY * 14 },
  { label: "30 days", value: ONE_DAY * 30 },
  { label: "365 days", value: ONE_DAY * 365 },
  { label: "Never", value: null }
];

function BlacklistServerWarning({ blacklist, currentServer }) {
  const affectsAllServers = blacklist.servers === null

  if (affectsAllServers) {
    return null;
  }

  let text = "";
  const affectsNone = blacklist.servers.length === 0;
  const failedToLoadCurrentServer = !("server_number" in currentServer);
  const affectsOnlyOtherServers = blacklist.servers.length > 0 && !blacklist.servers.includes(currentServer?.server_number ?? -1)

  if (affectsNone) {
    text = "This blacklist does not affect any servers!"
  }
  else if (failedToLoadCurrentServer) {
    text = `Failed to load current server information!\n`
    text += `This blacklist MAY NOT affect THIS server. Affected servers: [${blacklist.servers.join(", ")}]`
  }
  else if (affectsOnlyOtherServers) {
    text = `This blacklist DOES NOT affect THIS server! Affected servers: [${blacklist.servers.join(", ")}]`
  }

  return (
    <Typography variant="caption" color="secondary">
      {text}
    </Typography>
  )
}

const useStyles = makeStyles((theme) => ({
  selectEmpty: {
    marginTop: theme.spacing(2.7),
  },
}));

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
  const [punishMessages, setPunishMessages] = React.useState([])
  const [selectedMessage, setSelectedMessage] = React.useState("")
  const classes = useStyles();

  const handlePunishMessageChange = (event) => {
    setSelectedMessage(event.target.value ?? "")
    setReason(punishMessages[event.target.value] ?? "");
  };

  React.useEffect(() => {
    if (open) {
      const messageType = "punishments"
      getServerStatus().then(server => setCurrentServer(server)).catch(() => setCurrentServer({}))
      getSharedMessages(messageType).then(sharedMessages => {
        const locallyStoredMessages = new TextHistory(messageType).getTexts();
        setPunishMessages(sharedMessages.concat(locallyStoredMessages))
      })
    }
  }, [open])

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
          setSelectedMessage("")
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
            <BlacklistServerWarning blacklist={blacklist} currentServer={currentServer} />
            {/* PLAYER ID */}
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
            {/* EXPIRY */}
            <Grid container
              spacing={2}
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
                <Select
                  value={""}
                  onChange={(e) => {
                    e.target.value
                      ? setExpiresAt(moment().utc().add(e.target.value, 'seconds').format("YYYY-MM-DDTHH:mm"))
                      : setExpiresAt("");
                  }}
                  fullWidth
                  displayEmpty
                  className={classes.selectEmpty}
                >
                  <MenuItem value="">
                    <em>Preset Times</em>
                  </MenuItem>
                  {presetTimes.map(({ value, label }) => (
                    <MenuItem key={label} value={value}>{label}</MenuItem>
                  ))}
                </Select>
              </Grid>
            </Grid>
            {/* REASON */}
            <Grid container
              spacing={2}
              alignItems="top"
            >
              <Grid item xs={8}>
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
              </Grid>
              <Grid item xs={4}>
                <Select
                  id="saved-messages-select"
                  value={selectedMessage}
                  onChange={handlePunishMessageChange}
                  inputProps={{ 'aria-label': 'Saved Messages' }}
                  fullWidth
                  displayEmpty
                  className={classes.selectEmpty}
                >
                  <MenuItem value="">
                    <em>Saved Messages</em>
                  </MenuItem>
                  {punishMessages.map((message, i) => {
                    let label = message.substring(0, 16);
                    if (message.length > 16) {
                      label += "...";
                    }
                    return (
                      <MenuItem key={label + i} value={i}>{label}</MenuItem>
                    )
                  })}
                </Select>
              </Grid>
            </Grid>

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
