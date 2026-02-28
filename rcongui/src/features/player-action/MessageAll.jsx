import * as React from "react";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import {
  Alert,
  CircularProgress,
  IconButton,
  Stack,
  Tooltip,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { cmd } from "@/utils/fetchUtils";
import ErrorBrowser from "@/components/shared/ErrorBrowser";
import debug from "@/utils/debug";
import ThreePIcon from "@mui/icons-material/ThreeP";
import { MessageField } from "./fields/MessageField";

const logger = debug("MESSAGE ALL DIALOG");

export default function MessageAllDialog() {
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down("md"));

  const {
    mutate: messageAll,
    isPending,
    isSuccess,
    isError,
    error,
    reset,
  } = useMutation({
    mutationFn: async (data) =>
      cmd.MESSAGE_ALL_PLAYERS({
        payload: { message: data.message },
        throwRouteError: false,
      }),
    onMutate: async (variables) => {
      logger(
        "<START: Messaging all players>\n",
        "Content:\n",
        variables.message
      );
    },
    onSuccess: async () => {
      logger("<SUCCESS: Messaging all players>\n");
      setTimeout(handleDialogClose, 1250);
    },
    onError: async (error) => {
      console.error("<ERROR: Messaging all players>\n", error);
    },
  });

  const {
    handleSubmit,
    formState: { errors: formErrors },
    setValue,
    watch,
    control,
    ...formProps
  } = useForm({
    defaultValues: {
      reason: "",
    },
  });

  const handleDialogClickOpen = () => {
    reset();
    setValue("message", "");
    setDialogOpen(true);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
  };

  const handleFormSubmit = (data) => {
    // Handle the form submission with selected squads
    logger("Form data:", data);
    messageAll(data);
  };

  return (
    <React.Fragment>
      <Tooltip title={"Message All Players"}>
        <span>
          <IconButton onClick={handleDialogClickOpen}>
            <ThreePIcon />
          </IconButton>
        </span>
      </Tooltip>
      <Dialog
        open={dialogOpen}
        fullScreen={fullScreen}
        onClose={handleDialogClose}
        fullWidth
        slotProps={{
          paper: {
            component: "form",
            onSubmit: handleSubmit(handleFormSubmit),
          },
        }}
      >
        <DialogTitle>Message All Players</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {`This command will message all players on the server.`}
          </DialogContentText>
          <Stack spacing={2} marginTop={2}>
            {isError && (
              <ErrorBrowser
                errors={[
                  error?.message ??
                    "Something went wrong. Check the browser developer's tool > console for more information",
                ]}
                onClose={() => {}}
              />
            )}
            {isSuccess && (
              <Alert severity="success">Message sent to all players.</Alert>
            )}
            <MessageField
              control={control}
              errors={formErrors}
              setValue={setValue}
              {...formProps}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose} disabled={isPending}>
            Cancel
          </Button>
          {isPending ? (
            <Button disabled startIcon={<CircularProgress size={"1rem"} />}>
              Sending...
            </Button>
          ) : (
            <Button type="submit" disabled={isPending}>
              Confirm
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}
