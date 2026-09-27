import { lazy, Suspense, useState } from "react";
import { createPortal } from "react-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert, Box, Button, Checkbox, Chip, Dialog, DialogActions, DialogContent,
  DialogContentText, DialogTitle, FormControl, FormControlLabel, InputLabel,
  MenuItem, Paper, Select, Skeleton, Stack, TextField, Typography, useTheme,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import SyncIcon from "@mui/icons-material/Sync";
import emojiData from "@emoji-mart/data/sets/15/twitter.json";
import Emoji from "@/components/shared/Emoji";
import { toast } from "react-toastify";
import { cmd } from "@/utils/fetchUtils";
import { vipListQueryKeys } from "@/queries/vip-list-query";

const EmojiPicker = lazy(() => import("@emoji-mart/react"));

export function ImportPartnerListButton({ onCreated, serverNumber }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", source_url: "", token: "", webhook_url: "", approve_new: true, retention_days: null });
  const create = useMutation({
    mutationFn: (data) => cmd.CREATE_VIP_LIST_IMPORT({
      payload: { ...data, servers: Number.isInteger(serverNumber) ? [serverNumber] : null },
      throwRouteError: false,
    }),
    onSuccess: async (response) => {
      toast.success("Partner list connected. Synchronize it to preview new entries.");
      setOpen(false);
      setForm({ name: "", source_url: "", token: "", webhook_url: "", approve_new: true, retention_days: null });
      await onCreated(response?.result ?? response);
    },
    onError: (error) => toast.error(error.message),
  });

  return <>
    <Button variant="outlined" onClick={() => setOpen(true)}>Import partner list</Button>
    <Dialog open={open} onClose={() => !create.isPending && setOpen(false)} fullWidth maxWidth="sm">
      <DialogTitle>Import partner VIP list</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ pt: 1 }}>
          <TextField label="Local list name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <TextField label="Partner feed URL" value={form.source_url} onChange={(e) => setForm({ ...form, source_url: e.target.value })} helperText="HTTPS URL ending in /api/get_shared_vip_list" required />
          <TextField label="Partner share key" type="password" autoComplete="new-password" value={form.token} onChange={(e) => setForm({ ...form, token: e.target.value })} required />
          <TextField label="Discord webhook URL (optional)" type="url" autoComplete="off" value={form.webhook_url} onChange={(e) => setForm({ ...form, webhook_url: e.target.value })} />
          <TextField label="Delete inactive entries after days (optional)" type="number" value={form.retention_days ?? ""} onChange={(e) => setForm({ ...form, retention_days: e.target.value === "" ? null : Number(e.target.value) })} inputProps={{ min: 0, max: 3650 }} />
          <FormControlLabel control={<Checkbox checked={form.approve_new} onChange={(e) => setForm({ ...form, approve_new: e.target.checked })} />} label="Require approval for new partner VIPs" />
          <Alert severity="info">Partner records are read-only. Failed synchronization deactivates imported VIPs until the feed recovers.</Alert>
          <Typography variant="body2">Applies to {Number.isInteger(serverNumber) ? `server #${serverNumber}` : "all servers"}.</Typography>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setOpen(false)} disabled={create.isPending}>Cancel</Button>
        <Button variant="contained" onClick={() => create.mutate(form)} disabled={create.isPending || !form.name || !form.source_url || !form.token}>Connect</Button>
      </DialogActions>
    </Dialog>
  </>;
}

export function VipListPartnership({ list, canManageShares, canManageImports, onSynced, actionsContainer }) {
  const queryClient = useQueryClient();
  const theme = useTheme();
  const [name, setName] = useState("");
  const [shownToken, setShownToken] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [changeWebhook, setChangeWebhook] = useState(false);
  const [showFlagPicker, setShowFlagPicker] = useState(false);
  const [settings, setSettings] = useState({ name: "", approve_new: true, retention_days: null, webhook_url: "", clear_webhook: false, token: "", flags: [], max_duration_seconds: null });
  const shares = useQuery({
    queryKey: ["vip-list-shares", list.id],
    queryFn: () => cmd.GET_VIP_LIST_SHARES({ params: { vip_list_id: list.id } }),
    enabled: canManageShares && !list.is_imported,
  });
  const imports = useQuery({
    queryKey: ["vip-list-imports"],
    queryFn: () => cmd.GET_VIP_LIST_IMPORTS(),
    enabled: canManageImports && list.is_imported,
  });
  const createShare = useMutation({
    mutationFn: () => cmd.CREATE_VIP_LIST_SHARE({ payload: { vip_list_id: list.id, name }, throwRouteError: false }),
    onSuccess: (response) => {
      setShownToken(response?.result?.token ?? response?.token);
      setName("");
      queryClient.invalidateQueries({ queryKey: ["vip-list-shares", list.id] });
      queryClient.invalidateQueries({ queryKey: vipListQueryKeys.lists });
    },
    onError: (error) => toast.error(error.message),
  });
  const revoke = useMutation({
    mutationFn: (shareId) => cmd.REVOKE_VIP_LIST_SHARE({ payload: { share_id: shareId }, throwRouteError: false }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vip-list-shares", list.id] });
      queryClient.invalidateQueries({ queryKey: vipListQueryKeys.lists });
    },
    onError: (error) => toast.error(error.message),
  });
  const rotate = useMutation({
    mutationFn: (shareId) => cmd.ROTATE_VIP_LIST_SHARE({ payload: { share_id: shareId }, throwRouteError: false }),
    onSuccess: (response) => {
      setShownToken(response?.result?.token ?? response?.token);
      queryClient.invalidateQueries({ queryKey: ["vip-list-shares", list.id] });
      queryClient.invalidateQueries({ queryKey: vipListQueryKeys.lists });
    },
    onError: (error) => toast.error(error.message),
  });
  const sync = useMutation({
    mutationFn: () => cmd.SYNC_VIP_LIST_IMPORT({ payload: { vip_list_id: list.id }, throwRouteError: false }),
    onSuccess: (response) => {
      const counts = response?.result ?? response;
      toast.success(`${counts.new} new, ${counts.changed} changed, ${counts.deactivated} deactivated.`);
      onSynced();
      queryClient.invalidateQueries({ queryKey: ["vip-list-imports"] });
      queryClient.invalidateQueries({ queryKey: vipListQueryKeys.lists });
    },
    onError: (error) => toast.error(error.message),
  });
  const update = useMutation({
    mutationFn: async (data) => {
      const response = await cmd.EDIT_VIP_LIST_IMPORT({ payload: { vip_list_id: list.id, ...data }, throwRouteError: false });
      if ((response?.result ?? response)?.name !== data.name) {
        throw new Error("The server did not save the new list name. Rebuild and restart the backend.");
      }
      return response;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: vipListQueryKeys.lists });
      toast.success("Partner import settings updated.");
      setSettingsOpen(false);
      onSynced?.();
      queryClient.invalidateQueries({ queryKey: ["vip-list-imports"] });
    },
    onError: (error) => toast.error(error.message),
  });
  const source = (imports.data ?? []).find((item) => item.vip_list_id === list.id);
  const openSettings = () => {
    setSettings({ name: list.name, approve_new: source?.approve_new ?? true, retention_days: list.expired_retention_days, webhook_url: "", clear_webhook: false, token: "", flags: [...(list.flags ?? [])], max_duration_seconds: list.default_expiration_seconds });
    setChangeWebhook(false);
    setShowFlagPicker(false);
    setSettingsOpen(true);
  };
  const importActions = <>
    <Button startIcon={<SyncIcon />} onClick={() => sync.mutate()} disabled={sync.isPending}>Synchronize now</Button>
    <Button startIcon={<EditIcon />} onClick={openSettings}>Settings</Button>
  </>;

  if (list.is_imported && !canManageImports) return <Alert severity="info">This partner list is read-only.</Alert>;
  if (!list.is_imported && !canManageShares) return null;

  return <><Paper variant="outlined" sx={{ p: 2 }}>
    {list.is_imported ? <Stack spacing={1}>
      <Typography variant="h6">Partner import</Typography>
      <Typography variant="body2">Source: {source?.source_url ?? "Loading…"}</Typography>
      <Typography variant="body2">New records: {source?.approve_new ? "Approval required" : "Automatic"}</Typography>
      <Typography variant="body2">Last successful sync: {source?.last_success_at ? new Date(source.last_success_at).toLocaleString() : "Never"}</Typography>
      {source?.suspended_at && <Alert severity="error">Partner feed unavailable since {new Date(source.suspended_at).toLocaleString()}. Imported VIPs are inactive until a successful sync.</Alert>}
      <Typography variant="body2">Discord: {source?.webhook_configured ? "configured" : "off"}</Typography>
      {!actionsContainer && <Box>{importActions}</Box>}
    </Stack> : <Stack spacing={1}>
      <Typography variant="h6">Share this list</Typography>
      <Typography variant="body2">Each partner gets a separate, read-only key. The key is displayed once.</Typography>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
        <TextField size="small" label="Partner name" value={name} onChange={(e) => setName(e.target.value)} />
        <Button type="button" onClick={() => createShare.mutate()} disabled={!name.trim() || createShare.isPending}>Create key</Button>
      </Stack>
      {shownToken && <Alert severity="warning" onClose={() => setShownToken(null)}>
        Copy this key now: <Box component="code" sx={{ overflowWrap: "anywhere" }}>{shownToken}</Box>
        <Typography variant="body2">Feed URL: {`${window.location.origin}/api/get_shared_vip_list`}</Typography>
      </Alert>}
      {(shares.data ?? []).map((share) => <Stack key={share.id} direction="row" spacing={1} alignItems="center" flexWrap="wrap">
        <Typography variant="body2">{share.name}</Typography>
        <Typography variant="caption" color="text.secondary">
          Last used: {share.last_used_at ? new Date(share.last_used_at).toLocaleString() : "Never"}
        </Typography>
        {share.revoked_at ? (
          <Typography variant="caption" color="text.secondary">
            Revoked {new Date(share.revoked_at).toLocaleString()} by {share.revoked_by || "unknown (before tracking)"}
          </Typography>
        ) : share.expires_at && new Date(share.expires_at) <= new Date() ? (
          <Typography variant="caption" color="text.secondary">Expired {new Date(share.expires_at).toLocaleString()}</Typography>
        ) : (
          <>
            <Button type="button" size="small" disabled={rotate.isPending} onClick={() => {
              if (window.confirm(`Replace the key for ${share.name}? The current key stops working immediately.`)) rotate.mutate(share.id);
            }}>Rotate key</Button>
            <Button type="button" size="small" color="warning" disabled={rotate.isPending} onClick={() => revoke.mutate(share.id)}>Revoke</Button>
          </>
        )}
      </Stack>)}
    </Stack>}
  </Paper>
    {list.is_imported && actionsContainer && createPortal(importActions, actionsContainer)}
    <Dialog open={settingsOpen} onClose={() => !update.isPending && setSettingsOpen(false)} fullWidth maxWidth="sm">
      <DialogTitle>Edit partner VIP list</DialogTitle>
      <DialogContent><Stack spacing={2.5} sx={{ pt: 1 }}>
        <DialogContentText>Changes are stored in the CRCON database. Synchronize the partner feed to update its records.</DialogContentText>
        <TextField required autoFocus label="List name" value={settings.name} onChange={(e) => setSettings({ ...settings, name: e.target.value })} disabled={update.isPending} inputProps={{ maxLength: 255 }} />
        <FormControlLabel control={<Checkbox checked={settings.approve_new} onChange={(e) => setSettings({ ...settings, approve_new: e.target.checked })} />} label="Require approval for new entries" />
        <FormControl fullWidth disabled={update.isPending}>
          <InputLabel id="partner-list-expired-retention-label">Expired records</InputLabel>
          <Select labelId="partner-list-expired-retention-label" label="Expired records" value={settings.retention_days ?? "keep"} onChange={(e) => setSettings({ ...settings, retention_days: e.target.value === "keep" ? null : Number(e.target.value) })}>
            <MenuItem value="keep">Keep for manual review</MenuItem>
            <MenuItem value={0}>Delete automatically after expiration</MenuItem>
            <MenuItem value={1}>Delete after 1 day</MenuItem>
            <MenuItem value={7}>Delete after 7 days</MenuItem>
            <MenuItem value={30}>Delete after 30 days</MenuItem>
            {settings.retention_days !== null && ![0, 1, 7, 30].includes(settings.retention_days) && <MenuItem value={settings.retention_days}>Delete after {settings.retention_days} days</MenuItem>}
          </Select>
        </FormControl>
        <Typography variant="body2" color="text.secondary">Automatic cleanup runs periodically. Existing expired records are also removed when their retention time has passed.</Typography>
        <FormControl fullWidth disabled={update.isPending}>
          <InputLabel id="partner-list-duration-label">Maximum VIP duration</InputLabel>
          <Select labelId="partner-list-duration-label" label="Maximum VIP duration" value={settings.max_duration_seconds ?? "none"} onChange={(e) => setSettings({ ...settings, max_duration_seconds: e.target.value === "none" ? null : Number(e.target.value) })}>
            <MenuItem value="none">No local limit</MenuItem>
            <MenuItem value={0}>No local limit (never expires locally)</MenuItem>
            <MenuItem value={7200}>2 hours</MenuItem>
            <MenuItem value={86400}>1 day</MenuItem>
            <MenuItem value={604800}>7 days</MenuItem>
            <MenuItem value={2592000}>30 days</MenuItem>
            <MenuItem value={31536000}>1 year</MenuItem>
            {settings.max_duration_seconds != null && ![0, 7200, 86400, 604800, 2592000, 31536000].includes(settings.max_duration_seconds) && <MenuItem value={settings.max_duration_seconds}>Current: {settings.max_duration_seconds} seconds</MenuItem>}
          </Select>
        </FormControl>
        <Typography variant="body2" color="text.secondary">The earlier of the partner expiration and this local limit applies. The limit starts at first import.</Typography>
        <TextField label="New partner share key (optional)" type="password" autoComplete="new-password" value={settings.token} onChange={(e) => setSettings({ ...settings, token: e.target.value })} helperText="Leave blank to keep the current key. A new key is checked against the partner feed before saving." />
        <Stack spacing={1}>
          <Typography variant="subtitle1">Player flags</Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
            {settings.flags.map((flag) => <Chip key={flag} label={<Emoji emoji={flag} size={24} />} aria-label={`Remove flag ${flag}`} onDelete={update.isPending ? undefined : () => setSettings((current) => ({ ...current, flags: current.flags.filter((item) => item !== flag) }))} />)}
            <Button type="button" variant="outlined" disabled={update.isPending} onClick={() => setShowFlagPicker((value) => !value)}>{showFlagPicker ? "Close emoji picker" : "Add flag"}</Button>
          </Box>
          {showFlagPicker && <Suspense fallback={<Skeleton variant="rectangular" height={400} />}><Box sx={{ "& em-emoji-picker": { width: "100%" } }}><EmojiPicker set="twitter" theme={theme.palette.mode} dynamicWidth data={emojiData} onEmojiSelect={(emoji) => { setSettings((current) => ({ ...current, flags: current.flags.includes(emoji.native) ? current.flags : [...current.flags, emoji.native] })); setShowFlagPicker(false); }} /></Box></Suspense>}
          <Typography variant="body2" color="text.secondary">Active members receive these global player flags; manual flags are preserved.</Typography>
        </Stack>
        <FormControlLabel control={<Checkbox checked={changeWebhook} disabled={settings.clear_webhook} onChange={(e) => setChangeWebhook(e.target.checked)} />} label="Set new Discord webhook URL" />
        {changeWebhook && <TextField label="New Discord webhook URL" type="url" autoComplete="off" value={settings.webhook_url} onChange={(e) => setSettings({ ...settings, webhook_url: e.target.value })} required />}
        {source?.webhook_configured && <FormControlLabel control={<Checkbox checked={settings.clear_webhook} disabled={changeWebhook} onChange={(e) => setSettings({ ...settings, clear_webhook: e.target.checked })} />} label="Remove existing webhook" />}
      </Stack></DialogContent>
      <DialogActions>
        <Button onClick={() => setSettingsOpen(false)} disabled={update.isPending}>Cancel</Button>
        <Button variant="contained" onClick={() => update.mutate({ ...settings, name: settings.name.trim(), token: settings.token || undefined, webhook_url: changeWebhook ? settings.webhook_url : undefined })} disabled={update.isPending || !settings.name.trim() || (changeWebhook && !settings.webhook_url.trim())}>Save</Button>
      </DialogActions>
    </Dialog>
  </>;
}
