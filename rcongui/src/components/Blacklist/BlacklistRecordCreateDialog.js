import * as React from "react";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { FormControl, InputLabel, MenuItem, Select, Typography } from "@mui/material";
import moment from "moment";
import { getServerStatus, getSharedMessages } from "../../utils/fetchUtils";
import TextHistory from "../textHistory";
import { TimePickerButtons } from "../shared/time-picker-buttons";
import Grid from "@mui/material/Unstable_Grid2";


const presetTimes = [
  [1, "hour"],
  [1, "day"],
  [1, "week"],
  [1, "month"],
];

function BlacklistServerWarning({ blacklist, currentServer }) {
  const affectsAllServers = blacklist.servers === null;

  if (affectsAllServers) {
    return null;
  }

  let text = "";
  const affectsNone = blacklist.servers.length === 0;
  const failedToLoadCurrentServer = !("server_number" in currentServer);
  const affectsOnlyOtherServers =
    blacklist.servers.length > 0 &&
    !blacklist.servers.includes(currentServer?.server_number ?? -1);

  if (affectsNone) {
    text = "This blacklist does not affect any servers!";
  } else if (failedToLoadCurrentServer) {
    text = `Failed to load current server information!\n`;
    text += `This blacklist MAY NOT affect THIS server. Affected servers: [${blacklist.servers.join(
      ", "
    )}]`;
  } else if (affectsOnlyOtherServers) {
    text = `This blacklist DOES NOT affect THIS server! Affected servers: [${blacklist.servers.join(
      ", "
    )}]`;
  }

  return (
    <Typography variant="caption" color="secondary">
      {text}
    </Typography>
  );
}

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
  const [currentServer, setCurrentServer] = React.useState({});
  const [punishMessages, setPunishMessages] = React.useState([]);
  const [selectedMessage, setSelectedMessage] = React.useState("");

  const handlePunishMessageChange = (event) => {
    setSelectedMessage(event.target.value ?? "");
    setReason(punishMessages[event.target.value] ?? "");
  };

  React.useEffect(() => {
    if (open) {
      const messageType = "punishments";
      const locallyStoredMessages = new TextHistory(messageType).getTexts();
      setPunishMessages(locallyStoredMessages);

      getServerStatus()
        .then((server) => setCurrentServer(server))
        .catch(() => setCurrentServer({}));

      getSharedMessages(messageType).then((sharedMessages) => {
        setPunishMessages(sharedMessages.concat(locallyStoredMessages));
      });
    }
  }, [open]);

  React.useEffect(() => {
    if (initialValues) {
      if (initialValues.blacklistId !== undefined) {
        const blacklist = blacklists?.find(
          (b) => b.id === initialValues.blacklistId
        );
        if (blacklist) setBlacklist(blacklist);
      }
      if (initialValues.playerId !== undefined)
        setPlayerId(initialValues.playerId);
      if (initialValues.expiresAt !== undefined) {
        setExpiresAt(
          initialValues.expiresAt === null ? "" : initialValues.expiresAt
        );
      }
      if (initialValues.reason !== undefined) setReason(initialValues.reason);
    }
  }, [open]);

  React.useEffect(() => {
    if (blacklists?.length == 1) {
      setBlacklist(blacklists[0]);
    }
  });

  const handleClose = () => {
    setOpen(false);
    setBlacklist("");
    setPlayerId("");
    setExpiresAt("");
    setReason("");
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      PaperProps={{
        component: "form",
        onSubmit: (event) => {
          event.preventDefault();
          const data = {
            blacklistId: blacklist.id,
            playerId,
            expiresAt:
              expiresAt === "" ? null : moment(expiresAt).utc().toISOString(),
            reason,
          };
          onSubmit(data);
          setSelectedMessage("");
          handleClose();
        },
      }}
    >
      <DialogTitle>{titleText}</DialogTitle>
      <DialogContent>
        <DialogContentText>
          By blacklisting a player you are revoking their access to one or more
          servers.
        </DialogContentText>

        <FormControl required fullWidth>
          <InputLabel>Blacklist</InputLabel>
          <Select
            value={blacklist}
            onChange={(e) => setBlacklist(e.target.value)}
          >
            {blacklists?.map((b) => (
              <MenuItem key={b.id} value={b}>
                {b.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {blacklist && (
          <React.Fragment>
            <BlacklistServerWarning
              blacklist={blacklist}
              currentServer={currentServer}
            />
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
            <Grid container spacing={2} alignItems="center">
              <Grid xs={12}>
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
              <Grid xs={12}>
                {presetTimes.map(([amount, unit], index) => (
                  <TimePickerButtons
                    key={unit + index}
                    amount={amount}
                    unit={unit}
                    expirationTimestamp={expiresAt}
                    setExpirationTimestamp={(timestamp) => {
                      setExpiresAt(
                        moment(timestamp).format("YYYY-MM-DDTHH:mm")
                      );
                    }}
                  />
                ))}
              </Grid>
            </Grid>
            {/* REASON */}
            <Grid container spacing={2} alignItems="top">
              <Grid xs={8}>
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
              <Grid xs={4}>
                <Select
                  id="saved-messages-select"
                  value={selectedMessage}
                  onChange={handlePunishMessageChange}
                  inputProps={{ "aria-label": "Saved Messages" }}
                  fullWidth
                  displayEmpty
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
                      <MenuItem key={label + i} value={i}>
                        {label}
                      </MenuItem>
                    );
                  })}
                </Select>
              </Grid>
            </Grid>
          </React.Fragment>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button type="submit" disabled={blacklist === ""}>
          {submitText}
        </Button>
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
  );
}
