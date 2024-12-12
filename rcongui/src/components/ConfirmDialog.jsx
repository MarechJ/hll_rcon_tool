import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
  } from '@mui/material';
  import React from 'react';
  
  export const ConfirmDialog = ({ open, onConfirm, title, message }) => {
    const handleClose = () => {
      onConfirm(false);
    };
  
    const handleConfirm = () => {
      onConfirm(true);
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
        <DialogTitle>{title}</DialogTitle>
        <DialogContent dividers>{message}</DialogContent>
        <DialogActions>
          <Button onClick={handleClose} aria-label='Cancel'>Cancel</Button>
          <Button color="warning" onClick={handleConfirm} aria-label='Confirm'>
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    );
  };