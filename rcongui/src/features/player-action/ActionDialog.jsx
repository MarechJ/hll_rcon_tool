import {
  Alert,
  AlertTitle,
  AppBar,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Toolbar,
  Typography,
} from "@mui/material";
import React from "react";
import { ActionForm } from "./ActionForm";
import { useActionDialog } from "@/hooks/useActionDialog";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";
import CloseIcon from "@mui/icons-material/Close";

export const ActionDialog = () => {
  const { state, closeDialog } = useActionDialog();
  const submitRef = React.useRef();
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down("md"));
  const { open, action, recipients } = state;

  const handleLoading = (state) => {
    setLoading(state);
  };

  const handleClose = () => {
    setError(null);
    setLoading(false);
    closeDialog();
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
    setError,
    setLoading: handleLoading,
    closeDialog: handleClose,
  };

  if (!open) return null;

  return (
    <Dialog
      fullWidth
      fullScreen={fullScreen}
      open={open}
      onClose={handleClose}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <AppBar sx={{ position: "relative" }}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={handleClose}
            aria-label="close"
          >
            <CloseIcon />
          </IconButton>
          <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
            {action.name[0].toUpperCase() + action.name.substring(1)}
          </Typography>
          <Button
            color="warning"
            disabled={loading || !action || !recipients}
            onClick={handleConfirm}
            autoFocus
          >
            {loading ? "Processing..." : "Confirm"}
          </Button>
        </Toolbar>
      </AppBar>
      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 1 }}>
            <AlertTitle>{error?.name ?? "Error"}</AlertTitle>
            {error?.message ??
              "An error occured with your request. Open up your browser's console to investigate."}
          </Alert>
        )}
        {action.deprecated && (
          <Alert severity="info" sx={{ mb: 1 }}>
            <AlertTitle>Action deprecated</AlertTitle>
            {action.deprecationNote}
          </Alert>
        )}
        <Typography variant="subtitle1" sx={{ mb: 1 }}>
          {action.description}
        </Typography>
        <ActionForm actionHandlers={actionHandlers} state={state} />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          color="warning"
          disabled={loading || !action || !recipients}
          onClick={handleConfirm}
          autoFocus
        >
          {loading ? "Processing..." : "Confirm"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};