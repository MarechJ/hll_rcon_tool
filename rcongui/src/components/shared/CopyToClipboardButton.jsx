import { useClipboard } from "@/hooks/useClipboard";
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  Typography,
  Tooltip,
} from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DoneAllIcon from "@mui/icons-material/DoneAll";
import { useState } from "react";

export default function CopyToClipboardButton({ text, title, ...props }) {
  const { isClipboardAvailable, isCopied, copyToClipboard } = useClipboard();
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleClick = () => {
    if (isClipboardAvailable) {
      copyToClipboard(text);
    } else {
      setDialogOpen(true);
    }
  };

  return (
    <>
      <Tooltip title={title ?? null}>
        <Button
          variant="outlined"
          color="warning"
          onClick={handleClick}
          startIcon={isCopied ? <DoneAllIcon /> : <ContentCopyIcon />}
          {...props}
        >
          {isCopied ? "Copied!" : "Copy"}
        </Button>
      </Tooltip>
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogContent>
          <Typography>Copy to Clipboard only available with HTTPS</Typography>
        </DialogContent>
        <DialogContent>
          <Typography>{text}</Typography>
        </DialogContent>
      </Dialog>
    </>
  );
}
