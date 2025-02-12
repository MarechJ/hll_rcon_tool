import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from "@mui/material";
import { useState } from "react";

const ConfirmButton = ({
  onConfirm,
  title,
  description,
  buttonText,
  confirmText = "Confirm",
  cancelText = "Cancel",
  buttonProps = {},
  disabled = false,
}) => {
  const [open, setOpen] = useState(false);

  const handleConfirm = () => {
    onConfirm();
    setOpen(false);
  };

  return (
    <>
      <Button
        {...buttonProps}
        disabled={disabled}
        onClick={() => setOpen(true)}
      >
        {buttonText}
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        aria-labelledby="confirm-dialog-title"
        aria-describedby="confirm-dialog-description"
      >
        <DialogTitle id="confirm-dialog-title">{title}</DialogTitle>
        <DialogContent>
          <DialogContentText id="confirm-dialog-description">
            {description}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} color="warning">
            {cancelText}
          </Button>
          <Button onClick={handleConfirm} color="primary" autoFocus>
            {confirmText}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ConfirmButton; 