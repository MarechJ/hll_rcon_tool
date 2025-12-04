import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Checkbox from '@mui/material/Checkbox';
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { FormControl, FormControlLabel, FormGroup, InputLabel, MenuItem, Select, Typography } from "@mui/material";
import moment from "moment";
import { getServerStatus, getSharedMessages } from "@/utils/fetchUtils";
import TextHistory from "../textHistory";
import { TimePickerButtons } from "@/components/shared/TimePickerButtons";
import Grid from "@mui/material/Grid2";
import { Fragment, useEffect, useState } from "react";

const presetTimes = [
  [1, "hour"],
  [1, "day"],
  [1, "week"],
  [1, "month"],
];

function VipListServerWarning({ vipList, currentServer }) {
  const affectsAllServers = vipList.servers === null;

  if (affectsAllServers) {
    return null;
  }

  let text = "";
  const affectsNone = vipList.servers.length === 0;
  const failedToLoadCurrentServer = !("server_number" in currentServer);
  const affectsOnlyOtherServers =
    vipList.servers.length > 0 &&
    !vipList.servers.includes(currentServer?.server_number ?? -1);

  if (affectsNone) {
    text = "This VIP List does not affect any servers!";
  } else if (failedToLoadCurrentServer) {
    text = `Failed to load current server information!\n`;
    text += `This VIP List MAY NOT affect THIS server. Affected servers: [${vipList.servers.join(
      ", "
    )}]`;
  } else if (affectsOnlyOtherServers) {
    text = `This VIP List DOES NOT affect THIS server! Affected servers: [${vipList.servers.join(
      ", "
    )}]`;
  }

  return (
    <Typography variant="caption" color="secondary">
      {text}
    </Typography>
  );
}

export default function VipListRecordCreateDialog({
  open,
  setOpen,
  vipLists,
  onSubmit,
  initialValues,
  titleText = "VIP Player",
  submitText = "VIP Player",
  disablePlayerId,
  hasManyIDs = false,
}) {
  const [vipList, setVipList] = useState("");
  const [playerId, setPlayerId] = useState("");
  const [description, setDescription] = useState("");
  const [active, setActive] = useState(true);
  const [expiresAt, setExpiresAt] = useState("");
  const [notes, setNotes] = useState("");
  const [email, setEmail] = useState("");
  const [discordId, setDiscordId] = useState("");
  const [currentServer, setCurrentServer] = useState({});
  const [selectedMessage, setSelectedMessage] = useState("");

  useEffect(() => {
    if (open) {
      getServerStatus()
        .then((server) => setCurrentServer(server))
        .catch(() => setCurrentServer({}));
    }
  }, [open]);

  useEffect(() => {
    if (initialValues) {
      console.log(`${JSON.stringify(initialValues)}`)
      if (initialValues.vipListId !== undefined) {
        const vipList = vipLists?.find(
          (v) => v.id === initialValues.vipListId
        );
        if (vipList) setVipList(vipList);
      }
      if (initialValues.playerId !== undefined)
        setPlayerId(initialValues.playerId);
      if (initialValues.description !== undefined)
        setDescription(initialValues.description);
      if (initialValues.active !== undefined)
        setActive(initialValues.active);
      if (initialValues.expiresAt !== undefined) {
        setExpiresAt(
          initialValues.expiresAt === null ? "" : initialValues.expiresAt
        );
      }
      if (initialValues.notes !== undefined) setNotes(initialValues.notes);
      if (initialValues.email !== undefined) setEmail(initialValues.email);
      if (initialValues.discordId !== undefined) setDiscordId(initialValues.discordId);
    }
  }, [open]);

  useEffect(() => {
    if (vipLists?.length == 1) {
      setVipList(vipLists[0]);
    }
  });

  const handleClose = () => {
    setOpen(false);
    setVipList("");
    setPlayerId("");
    setDescription("");
    setActive(true);
    setExpiresAt("");
    setNotes("");
    setEmail("");
    setDiscordId("");
  };

  return (
    (<Dialog
      open={open}
      onClose={handleClose}
      PaperProps={{
        component: "form",
        onSubmit: (event) => {
          event.preventDefault();
          const data = {
            vipListId: vipList.id,
            playerId,
            description: description === "" ? null : description,
            active,
            expiresAt:
              expiresAt === "" ? null : moment(expiresAt).utc().toISOString(),
            notes: notes === "" ? null : notes,
            email: email === "" ? null : email,
            discordId: discordId === "" ? null : discordId,
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
          Granting VIP to a player allows them to join the game server ahead of non VIP players.
        </DialogContentText>

        <FormControl required fullWidth>
          <InputLabel>VIP List</InputLabel>
          <Select
            value={vipList}
            onChange={(e) => setVipList(e.target.value)}
          >
            {vipLists?.map((v) => (
              <MenuItem key={v.id} value={v}>
                {v.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {vipList && (
          <Fragment>
            <VipListServerWarning
              vipList={vipList}
              currentServer={currentServer}
            />
            {/* Player ID */}
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
            {/* active */}
            <FormGroup>
              <FormControlLabel control={<Checkbox checked={active} id='active' onChange={(e) => setActive(e.target.value)} />} label="Active" />
            </FormGroup>
            {/* expiresAt */}
            <Grid container spacing={2} alignItems="center">
              <Grid size={12}>
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
              <Grid size={12}>
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
            {/* email */}
            <TextField
              margin="dense"
              id="email"
              name="email"
              label="E-Mail"
              type="text"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              fullWidth
              variant="standard"
            />
            {/* email */}
            <TextField
              margin="dense"
              id="discord_id"
              name="discord_id"
              label="Discord ID"
              type="text"
              value={discordId}
              onChange={(e) => setDiscordId(e.target.value)}
              fullWidth
              variant="standard"
            />
            {/* description */}
            <TextField
              multiline
              margin="dense"
              id="description"
              name="description"
              label="Description"
              // type="reason"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              fullWidth
              variant="standard"
            //     helperText="Available variables:
            // {player_id}, {player_name}, {banned_at}, {banned_until}, {expires_at},
            // {duration}, {expires}, {ban_id}, {blacklist_name}"
            />
            <TextField
              multiline
              margin="dense"
              id="notes"
              name="notes"
              label="Notes"
              // type="reason"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              fullWidth
              variant="standard"
            //     helperText="Available variables:
            // {player_id}, {player_name}, {banned_at}, {banned_until}, {expires_at},
            // {duration}, {expires}, {ban_id}, {blacklist_name}"
            />
          </Fragment>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button type="submit" disabled={vipList === ""}>
          {submitText}
        </Button>
      </DialogActions>
    </Dialog>)
  );
}

export function VipListRecordCreateButton({
  vipLists,
  onSubmit,
  initialValues,
  disablePlayerId,
  children,
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
        {children}
      </Button>
      <VipListRecordCreateDialog
        open={open}
        setOpen={setOpen}
        vipLists={vipLists}
        onSubmit={onSubmit}
        initialValues={initialValues}
        disablePlayerId={disablePlayerId}
      />
    </Fragment>
  );
}
