import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert, Box, Button, Checkbox, Dialog, DialogActions, DialogContent,
  DialogTitle, FormControlLabel, Paper, Stack, TextField, Typography,
} from "@mui/material";
import { toast } from "react-toastify";
import { cmd } from "@/utils/fetchUtils";
import { vipListQueryKeys } from "@/queries/vip-list-query";

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
          <Alert severity="info">Partner records are read-only. Failed updates keep the current entries.</Alert>
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

export function VipListPartnership({ list, canManageShares, canManageImports, onSynced }) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [shownToken, setShownToken] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [changeWebhook, setChangeWebhook] = useState(false);
  const [settings, setSettings] = useState({ approve_new: true, retention_days: null, webhook_url: "", clear_webhook: false, token: "", flags: "", max_duration_days: "" });
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
    mutationFn: (data) => cmd.EDIT_VIP_LIST_IMPORT({ payload: { vip_list_id: list.id, ...data }, throwRouteError: false }),
    onSuccess: () => {
      toast.success("Partner import settings updated.");
      setSettingsOpen(false);
      queryClient.invalidateQueries({ queryKey: ["vip-list-imports"] });
      queryClient.invalidateQueries({ queryKey: vipListQueryKeys.lists });
    },
    onError: (error) => toast.error(error.message),
  });
  const source = (imports.data ?? []).find((item) => item.vip_list_id === list.id);

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
      <Box>
        <Button onClick={() => sync.mutate()} disabled={sync.isPending}>Synchronize now</Button>
        <Button onClick={() => {
          setSettings({ approve_new: source?.approve_new ?? true, retention_days: list.expired_retention_days, webhook_url: "", clear_webhook: false, token: "", flags: (list.flags ?? []).join(", "), max_duration_days: list.default_expiration_seconds ? list.default_expiration_seconds / 86400 : "" });
          setChangeWebhook(false);
          setSettingsOpen(true);
        }}>Settings</Button>
      </Box>
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
    <Dialog open={settingsOpen} onClose={() => !update.isPending && setSettingsOpen(false)} fullWidth maxWidth="sm">
      <DialogTitle>Partner import settings</DialogTitle>
      <DialogContent><Stack spacing={2} sx={{ pt: 1 }}>
        <FormControlLabel control={<Checkbox checked={settings.approve_new} onChange={(e) => setSettings({ ...settings, approve_new: e.target.checked })} />} label="Require approval for new entries" />
        <TextField label="Delete inactive entries after days" type="number" value={settings.retention_days ?? ""} onChange={(e) => setSettings({ ...settings, retention_days: e.target.value === "" ? null : Number(e.target.value) })} inputProps={{ min: 0, max: 3650 }} />
        <TextField label="New partner share key (optional)" type="password" autoComplete="new-password" value={settings.token} onChange={(e) => setSettings({ ...settings, token: e.target.value })} helperText="Leave blank to keep the current key. A new key is checked against the partner feed before saving." />
        <TextField label="Player flags (comma-separated)" value={settings.flags} onChange={(e) => setSettings({ ...settings, flags: e.target.value })} helperText="Applied to active players in this imported list." />
        <TextField label="Maximum VIP duration (days)" type="number" value={settings.max_duration_days} onChange={(e) => setSettings({ ...settings, max_duration_days: e.target.value })} inputProps={{ min: 0, max: 3650, step: 1 }} helperText="Optional local limit from the first import; the partner's earlier expiry still applies." />
        <FormControlLabel control={<Checkbox checked={changeWebhook} disabled={settings.clear_webhook} onChange={(e) => setChangeWebhook(e.target.checked)} />} label="Set new Discord webhook URL" />
        {changeWebhook && <TextField label="New Discord webhook URL" type="url" autoComplete="off" value={settings.webhook_url} onChange={(e) => setSettings({ ...settings, webhook_url: e.target.value })} required />}
        {source?.webhook_configured && <FormControlLabel control={<Checkbox checked={settings.clear_webhook} disabled={changeWebhook} onChange={(e) => setSettings({ ...settings, clear_webhook: e.target.checked })} />} label="Remove existing webhook" />}
      </Stack></DialogContent>
      <DialogActions>
        <Button onClick={() => setSettingsOpen(false)} disabled={update.isPending}>Cancel</Button>
        <Button onClick={() => update.mutate({ ...settings, token: settings.token || undefined, flags: settings.flags.split(",").map((flag) => flag.trim()).filter(Boolean), max_duration_seconds: settings.max_duration_days === "" ? null : Math.round(Number(settings.max_duration_days) * 86400), webhook_url: changeWebhook ? settings.webhook_url : undefined })} disabled={update.isPending || (changeWebhook && !settings.webhook_url.trim())}>Save</Button>
      </DialogActions>
    </Dialog>
  </>;
}
