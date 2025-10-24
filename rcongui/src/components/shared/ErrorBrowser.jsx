import React from "react";
import {
  Alert,
  AlertTitle,
  Box,
  IconButton,
  Stack,
  Typography,
} from "@mui/material";
import ArrowLeftIcon from "@mui/icons-material/ArrowLeft";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";

const ErrorBrowser = ({ errors, onClose }) => {
  const [open, setOpen] = React.useState(true);
  const [active, setActive] = React.useState(0);

  const handleClose = () => {
    setOpen(false)
    onClose()
  }

  if (!open || !errors || errors.length === 0) return null;

  return (
    <Alert
      severity="error"
      onClose={handleClose}
    >
      <AlertTitle>
        <Stack direction={"row"} gap={1} alignItems={"center"}>
          <IconButton
            aria-label="previous"
            size="small"
            onClick={() => setActive((prev) => Math.max(0, prev - 1))}
            disabled={active === 0}
          >
            <ArrowLeftIcon fontSize="inherit" />
          </IconButton>
          <Typography variant="subtitle2">
            Error {`(${active + 1}/${errors.length})`}
          </Typography>
          <IconButton
            aria-label="next"
            size="small"
            onClick={() =>
              setActive((prev) => Math.min(errors.length - 1, prev + 1))
            }
            disabled={active === errors.length - 1}
          >
            <ArrowRightIcon fontSize="inherit" />
          </IconButton>
        </Stack>
      </AlertTitle>
      <Typography>{errors[active]}</Typography>
    </Alert>
  );
};

export default ErrorBrowser;
