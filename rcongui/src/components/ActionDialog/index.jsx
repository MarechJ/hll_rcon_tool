import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import React from 'react';
import { ActionForm } from './ActionForm';
import { useActionDialog } from '../../hooks/useActionDialog';

export const ActionDialog = () => {
  const { open, setOpen, action, recipients } = useActionDialog();
  const submitRef = React.useRef();

  const handleClose = () => {
    setOpen(false);
  };

  const handleConfirm = () => {
    submitRef.current.click();
  };

  if (!open) return null;

  return (
    <Dialog
      fullWidth
      maxWidth={'sm'}
      open={open}
      onClose={handleClose}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle>
        {action.name[0].toUpperCase() + action.name.substring(1)}
      </DialogTitle>
      <DialogContent dividers>
        <Alert severity="info" sx={{ mb: 1 }}>
          {action.description}
        </Alert>
        <ActionForm
          submitRef={submitRef}
          action={action}
          recipients={recipients}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button color="warning" onClick={handleConfirm}>
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
  );
};
