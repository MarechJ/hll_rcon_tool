import {
  Alert,
  AlertTitle,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from "@mui/material";
import React from "react";
import { ActionForm } from "./ActionForm";
import { useActionDialog } from "@/hooks/useActionDialog";

export const ActionDialog = () => {
  const { open, setOpen, action, recipients } = useActionDialog();
  const submitRef = React.useRef();
  const [loading, setLoading] = React.useState(false);

  const handleLoading = (state) => {
    setLoading(state);
  };

  const handleClose = () => {
    setOpen(false);
    setLoading(false)
  };

  const handleConfirm = () => {
    submitRef.current.click();
  };

  React.useEffect(() => {
    return () => {
      setLoading(false);
    };
  }, []);

  const actionHandlers = {
    submitRef,
    setLoading: handleLoading,
    closeDialog: handleClose,
  };

  if (!open) return null;

  return (
    <Dialog
      fullWidth
      open={open}
      onClose={handleClose}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      {action && action.name ? (
        <>
          <DialogTitle>
            {action.name[0].toUpperCase() + action.name.substring(1)}
          </DialogTitle>
          <DialogContent dividers>
            {action.deprecated && (
              <Alert severity="info" sx={{ mb: 1 }}>
                <AlertTitle>Action deprecated</AlertTitle>
                {action.deprecationNote}
              </Alert>
            )}
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              {action.description}
            </Typography>
            <ActionForm actionHandlers={actionHandlers} action={action} recipients={recipients} />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button color="warning" disabled={loading || !action || !recipients} onClick={handleConfirm} autoFocus>
              {loading ? 'Processing...' : 'Confirm'}
            </Button>
          </DialogActions>
        </>
      ) : (
        <Typography variant="h6">Action not available</Typography>
      )}
    </Dialog>
  );
};
