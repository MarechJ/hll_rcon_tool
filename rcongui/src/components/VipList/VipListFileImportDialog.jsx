import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import { InputFileUpload } from "@/components/shared/InputFileUpload";

const API_URL = process.env.REACT_APP_API_URL;

const requestImport = async (endpoint, vipListId, file, mode) => {
  const formData = new FormData();
  formData.append("vip_list_id", vipListId);
  formData.append("mode", mode);
  formData.append("file", file);

  const response = await fetch(`${API_URL}${endpoint}`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("The server did not return a valid response.");
  }

  if (!response.ok || data?.failed) {
    throw new Error(data?.error || "The VIP list import failed.");
  }

  return data?.result ?? data;
};

export default function VipListFileImportDialog({
  open,
  vipList,
  onClose,
  onImported,
}) {
  const [file, setFile] = useState(null);
  const [mode, setMode] = useState("merge");
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!open) {
      setFile(null);
      setMode("merge");
      setPreview(null);
      setLoading(false);
      setError(null);
    }
  }, [open]);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0] ?? null;

    setFile(selectedFile);
    setPreview(null);
    setError(null);

    // Allow selecting the same file again.
    event.target.value = "";
  };

  const handleModeChange = (event) => {
    setMode(event.target.value);
    setPreview(null);
    setError(null);
  };

  const handlePreview = async () => {
    if (!vipList || !file) return;

    setLoading(true);
    setError(null);

    try {
      const result = await requestImport(
        "preview_vip_list_import_file",
        vipList.id,
        file,
        mode
      );
      setPreview(result);
    } catch (err) {
      setPreview(null);
      setError(err?.message || "Unable to preview the VIP list import.");
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!vipList || !file || !preview) return;

    setLoading(true);
    setError(null);

    try {
      const result = await requestImport(
        "import_vip_list_file",
        vipList.id,
        file,
        mode
      );

      await onImported?.(result);
      onClose();
    } catch (err) {
      setError(err?.message || "Unable to import the VIP list.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={loading ? undefined : onClose} fullWidth maxWidth="sm">
      <DialogTitle>
        Import VIP records{vipList ? ` into ${vipList.name}` : ""}
      </DialogTitle>

      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <Typography color="text.secondary">
            Import VIP records from a legacy text file or CSV file.
          </Typography>

          <InputFileUpload
            text={file ? file.name : "Select import file"}
            accept=".txt,.csv,text/plain,text/csv"
            onChange={handleFileChange}
            disabled={loading}
          />

          <FormControl fullWidth disabled={loading}>
            <InputLabel id="vip-import-mode-label">Import mode</InputLabel>
            <Select
              labelId="vip-import-mode-label"
              value={mode}
              label="Import mode"
              onChange={handleModeChange}
            >
              <MenuItem value="merge">Merge</MenuItem>
              <MenuItem value="replace">Replace</MenuItem>
            </Select>
          </FormControl>

          {mode === "merge" && (
            <Alert severity="info">
              Merge adds new records and updates matching records. Existing
              records that are not present in the file are left unchanged.
            </Alert>
          )}

          {mode === "replace" && (
            <Alert severity="warning">
              Replace deactivates records in this VIP list that are not present
              in the imported file. Records in other VIP lists are not affected.
            </Alert>
          )}

          {error && <Alert severity="error">{error}</Alert>}

          {preview && (
            <Stack spacing={1}>
              <Typography variant="subtitle1">Preview</Typography>

              <Typography>
                {preview.total} record(s) processed: {preview.ready} ready,{" "}
                {preview.pending} pending, {preview.conflicts} conflict(s).
              </Typography>

              <Typography color="text.secondary">
                {preview.created} create, {preview.updated} update,{" "}
                {preview.unchanged} unchanged
                {mode === "replace"
                  ? `, ${preview.deactivated} deactivate`
                  : ""}
                .
              </Typography>

              {(preview.pending_created > 0 ||
                preview.pending_updated > 0 ||
                preview.pending_unchanged > 0 ||
                preview.pending_removed > 0) && (
                <Typography color="text.secondary">
                  Pending: {preview.pending_created} create,{" "}
                  {preview.pending_updated} update,{" "}
                  {preview.pending_unchanged} unchanged,{" "}
                  {preview.pending_removed} remove.
                </Typography>
              )}

              {preview.conflicts > 0 && (
                <Alert severity="warning">
                  {preview.conflicts} record(s) have identity conflicts and
                  cannot be imported automatically.
                </Alert>
              )}

              {preview.pending > 0 && (
                <Alert severity="info">
                  {preview.pending} record(s) require identity resolution and
                  will remain pending until they can be matched safely.
                </Alert>
              )}
            </Stack>
          )}
        </Stack>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>

        {!preview ? (
          <Button
            variant="contained"
            onClick={handlePreview}
            disabled={!file || loading}
          >
            {loading ? <CircularProgress size={20} /> : "Preview"}
          </Button>
        ) : (
          <>
            <Button
              onClick={() => setPreview(null)}
              disabled={loading}
            >
              Back
            </Button>

            <Button
              variant="contained"
              onClick={handleImport}
              disabled={loading}
            >
              {loading ? <CircularProgress size={20} /> : "Confirm import"}
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
}
