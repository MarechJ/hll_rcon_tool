import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { Alert, Chip, Divider, FormControl, InputLabel, MenuItem, Paper, Select, Stack, Typography } from "@mui/material";
import { cmd } from "@/utils/fetchUtils";
import { TimePickerButtons } from "@/components/shared/TimePickerButtons";
import Grid from "@mui/material/Grid2";
import {Fragment, useEffect, useState} from "react";
import { useQuery } from "@tanstack/react-query";
import { useTemplates } from "@/hooks/useTemplates";
import dayjs from 'dayjs';
import { DesktopDateTimePicker } from '@mui/x-date-pickers/DesktopDateTimePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import PlayerSearchField from "@/components/form/custom/PlayerSearchField";

const presetTimes = [
  [2, "hours"],
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

  return text ? <Alert severity="warning" sx={{ whiteSpace: "pre-line" }}>{text}</Alert> : null;
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
  const [blacklist, setBlacklist] = useState("");
  const [playerName, setPlayerName] = useState("");
  const [playerId, setPlayerId] = useState("");
  const [expiresAt, setExpiresAt] = useState(dayjs());
  const [reason, setReason] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [selectedPlayers, setSelectedPlayers] = useState([]);
  const reasonTemplates = useTemplates("reason");

  const { data: currentServer = {} } = useQuery({
    queryKey: [{ queryIdentifier: "get_connection_info" }],
    queryFn: () => cmd.GET_CRCON_SERVER_CONNECTION(),
    enabled: open,
    staleTime: 60_000,
  });
  const handleTemplateChange = (event) => {
    const value = event.target.value ?? "";
    setSelectedTemplate(value);
    if (value !== "") setReason(reasonTemplates[Number(value)].content);
  };

  const addSelectedPlayer = (player) => {
    const id = player?.player_id?.trim();
    if (!id) return;
    const name = player?.names?.[0]?.name ?? player?.name ?? id;
    setSelectedPlayers((current) =>
      current.some((selected) => selected.player_id === id)
        ? current
        : [...current, { player_id: id, name }]
    );
    setPlayerName("");
    setPlayerId("");
  };

  useEffect(() => {
    if (initialValues) {
      if (initialValues.blacklistId !== undefined) {
        const blacklist = blacklists?.find(
          (b) => b.id === initialValues.blacklistId
        );
        if (blacklist) setBlacklist(blacklist);
      }
      if (initialValues.playerId !== undefined) setPlayerId(initialValues.playerId);
      if (initialValues.expiresAt !== undefined) {
        setExpiresAt(
          initialValues.expiresAt === null ? null : dayjs(initialValues.expiresAt)
        );
      }
      if (initialValues.reason !== undefined) setReason(initialValues.reason);
    } else {
      setExpiresAt(dayjs());
    }
  }, [open]);

  const handleClose = () => {
    setOpen(false);
    setBlacklist("");
    setPlayerName("");
    setPlayerId("");
    setExpiresAt(dayjs());
    setReason("");
    setSelectedTemplate("");
    setSelectedPlayers([]);
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      fullWidth
      maxWidth="sm"
      PaperProps={{
        component: "form",
        sx: { borderRadius: 2 },
        onSubmit: (event) => {
          event.preventDefault();
          if (!blacklist) return;
          const playerIds = Array.from(new Set([
            ...selectedPlayers.map((player) => player.player_id),
            ...(playerId.trim() && playerName.trim() ? [playerId.trim()] : []),
          ]));
          const data = {
            blacklistId: blacklist.id,
            playerId: playerIds[0] ?? playerId,
            playerIds,
            expiresAt,
            reason,
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
            By blacklisting a player you are revoking their access to one or more servers.
          </DialogContentText>

          <FormControl required fullWidth>
            <InputLabel id="blacklist-record-list-label">Blacklist</InputLabel>
            <Select
              labelId="blacklist-record-list-label"
              label="Blacklist"
              value={blacklist}
              onChange={(e) => setBlacklist(e.target.value)}
            >
              {blacklists?.map((b) => (
                <MenuItem key={b.id} value={b}>{b.name}</MenuItem>
              ))}
            </Select>
          </FormControl>

          {blacklist && (
            <BlacklistServerWarning blacklist={blacklist} currentServer={currentServer} />
          )}
              {hasManyIDs ? (
                <TextField
                  required
                  multiline
                  minRows={3}
                  id="playerId"
                  name="playerId"
                  label="Player IDs"
                  value={playerId}
                  onChange={(e) => setPlayerId(e.target.value)}
                  fullWidth
                  disabled={disablePlayerId}
                />
              ) : (
                <PlayerSearchField
                  required={selectedPlayers.length === 0}
                  nameValue={playerName}
                  onNameInputChange={setPlayerName}
                  idValue={playerId}
                  onIdInputChange={setPlayerId}
                  onSelect={addSelectedPlayer}
                  addButtonFullWidth
                  disabled={disablePlayerId}
                  direction="column"
                />
              )}
              {!disablePlayerId && selectedPlayers.length > 0 && (
                <Stack direction="row" gap={0.75} flexWrap="wrap" useFlexGap>
                  {selectedPlayers.map((player) => (
                    <Chip
                      key={player.player_id}
                      label={player.name === player.player_id ? player.player_id : `${player.name} · ${player.player_id}`}
                      onDelete={() => setSelectedPlayers((current) =>
                        current.filter((selected) => selected.player_id !== player.player_id)
                      )}
                    />
                  ))}
                </Stack>
              )}

              <Paper variant="outlined" sx={{ p: 2, bgcolor: "background.default" }}>
                <Stack spacing={1.5}>
                  <Typography variant="subtitle1" fontWeight={600}>Expiration</Typography>
                  {expiresAt !== null ? (
                    <LocalizationProvider dateAdapter={AdapterDayjs}>
                      <DesktopDateTimePicker
                        onChange={(value) => setExpiresAt(value)}
                        value={expiresAt}
                        id="expiresAt"
                        name="expiresAt"
                        format="LLL"
                        ampm={false}
                        slotProps={{ textField: { helperText: "The date this action will expire.", fullWidth: true } }}
                        maxDate={dayjs("3000-01-01T00:00:00+00:00")}
                        disablePast={!disablePlayerId}
                      />
                    </LocalizationProvider>
                  ) : (
                    <Alert severity="info">This blacklist record never expires.</Alert>
                  )}
                  <Grid container spacing={1}>
                    {presetTimes.map(([amount, unit], index) => (
                      <Grid key={unit + index} size={{ xs: 12, sm: 6 }}>
                        <TimePickerButtons
                          amount={amount}
                          unit={unit}
                          expirationTimestamp={expiresAt ?? dayjs()}
                          setExpirationTimestamp={setExpiresAt}
                        />
                      </Grid>
                    ))}
                  </Grid>
                  <Button variant="outlined" color="secondary" onClick={() => setExpiresAt(null)}>
                    Never expires
                  </Button>
                </Stack>
              </Paper>

              <Divider />
              <Stack spacing={1.5}>
                <TextField
                  required
                  multiline
                  rows={5}
                  id="reason"
                  name="reason"
                  label="Reason"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  fullWidth
                  helperText="Available variables: {player_id}, {player_name}, {banned_at}, {banned_until}, {expires_at}, {duration}, {expires}, {ban_id}, {blacklist_name}"
                />
                <FormControl fullWidth>
                  <InputLabel id="blacklist-reason-template-label">Reason template</InputLabel>
                  <Select
                    labelId="blacklist-reason-template-label"
                    id="saved-reasons-select"
                    label="Reason template"
                    value={selectedTemplate}
                    onChange={handleTemplateChange}
                  >
                    <MenuItem value=""><em>Select a saved reason</em></MenuItem>
                    {reasonTemplates.map((template, index) => (
                      <MenuItem key={template.id} value={String(index)}>{template.title}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Stack>
        </Stack>
      </DialogContent>
      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={handleClose}>Cancel</Button>
        <Button variant="contained" type="submit" disabled={blacklist === ""}>
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
      <BlacklistRecordCreateDialog
        open={open}
        setOpen={setOpen}
        blacklists={blacklists}
        onSubmit={onSubmit}
        initialValues={initialValues}
        disablePlayerId={disablePlayerId}
      />
    </Fragment>
  );
}
