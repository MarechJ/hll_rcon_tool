import React from "react";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Chip from "@mui/material/Chip";
import { Stack, Alert, CircularProgress } from "@mui/material";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { cmd } from "@/utils/fetchUtils";
import CheckIcon from "@mui/icons-material/Check";
import ErrorIcon from "@mui/icons-material/Error";
import { ControlledTextInput } from "@/components/form/core/ControlledTextInput";
import { ControlledSelect } from "@/components/form/core/ControlledSelect";

function EditSoldierButton({ Icon, playerId, currentSoldierData }) {
  const [open, setOpen] = React.useState(false);
  const [submitStatus, setSubmitStatus] = React.useState(null); // null, 'success', 'error'
  const [errorMessage, setErrorMessage] = React.useState("");
  const queryClient = useQueryClient();

  // Platform options based on Platform.jsx cases
  const platformOptions = [
    { value: "steam", label: "Steam" },
    { value: "epic", label: "Epic" },
    { value: "xbl", label: "Xbox Live" },
    { value: "xsx", label: "Xbox Series X/S" },
    { value: "psn", label: "PlayStation Network" },
    { value: "ps5", label: "PlayStation 5" },
  ];

  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
    ...formProps
  } = useForm({
    defaultValues: {
      name: currentSoldierData?.name || "",
      level: currentSoldierData?.level || "",
      platform: currentSoldierData?.platform || "",
      clan_tag: currentSoldierData?.clan_tag || "",
      eos_id: currentSoldierData?.eos_id || "",
    },
  });

  const { mutate: editPlayerSoldier, isPending } = useMutation({
    mutationFn: async (data) => {
      // Convert empty strings to null and level to number
      const payload = {
        player_id: playerId,
        name: data.name || null,
        level: data.level ? parseInt(data.level, 10) : null,
        platform: data.platform || null,
        clan_tag: data.clan_tag || null,
        eos_id: data.eos_id || null,
      };
      
      return cmd.EDIT_PLAYER_SOLDIER({
        payload,
        throwRouteError: false,
      });
    },
    onSuccess: (data) => {
      setSubmitStatus('success');
      // Invalidate and refetch player profile data
      queryClient.invalidateQueries({ queryKey: ['player-profile', playerId] });
      // Close dialog after a short delay
      setTimeout(() => {
        setOpen(false);
        setSubmitStatus(null);
        reset();
      }, 2000);
    },
    onError: (error) => {
      setSubmitStatus('error');
      setErrorMessage(error.message || 'Failed to update player soldier information');
    },
  });

  const handleClickOpen = () => {
    setOpen(true);
    setSubmitStatus(null);
    setErrorMessage("");
    // Reset form with current values
    reset({
      name: currentSoldierData?.name || "",
      level: currentSoldierData?.level || "",
      platform: currentSoldierData?.platform || "",
      clan_tag: currentSoldierData?.clan_tag || "",
      eos_id: currentSoldierData?.eos_id || "",
    });
  };

  const handleClose = () => {
    setOpen(false);
    setSubmitStatus(null);
    setErrorMessage("");
    reset();
  };

  const onSubmit = (data) => {
    setSubmitStatus(null);
    setErrorMessage("");
    editPlayerSoldier(data);
  };

  // Check if fields should be disabled
  const isNameDisabled = currentSoldierData?.name && currentSoldierData.name.trim() !== "";
  const isLevelDisabled = currentSoldierData?.level && currentSoldierData.level > 0;
  const isPlatformDisabled = currentSoldierData?.platform && currentSoldierData.platform.trim() !== "";
  const isClanTagDisabled = currentSoldierData.clan_tag !== null;
  const isEosIdDisabled = currentSoldierData?.eos_id && currentSoldierData.eos_id.trim() !== "";
  return (
    <React.Fragment>
      <Chip
        icon={<Icon />}
        label={"unset"}
        variant="outlined"
        size="small"
        onClick={handleClickOpen}
      />
      <Dialog
        open={open}
        onClose={handleClose}
        slotProps={{
          paper: {
            component: "form",
            onSubmit: handleSubmit(onSubmit),
          },
        }}
      >
        <DialogTitle>Update Player Soldier Information</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Fill in the missing soldier information. Fields with existing values are disabled and cannot be modified.
          </DialogContentText>
          
          {submitStatus === 'success' && (
            <Alert severity="success" sx={{ mt: 2 }}>
              <CheckIcon sx={{ mr: 1 }} />
              Successfully updated soldier information!
            </Alert>
          )}
          
          {submitStatus === 'error' && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <ErrorIcon sx={{ mr: 1 }} />
              {errorMessage}
            </Alert>
          )}

          <Stack spacing={2} sx={{ mt: 2 }}>
            <ControlledTextInput
              error={errors.name}
              control={control}
              name="name"
              label="Player Name"
              disabled={isPending || isNameDisabled}
              rules={{
                pattern: {
                  value: /^[a-zA-Z0-9\s\-_]+$/,
                  message: "Name can only contain letters, numbers, spaces, hyphens, and underscores"
                }
              }}
              helperText={
                isNameDisabled ? "This field already has a value and cannot be modified" : "The player's in-game name"
              }
              fullWidth
            />
            
            <ControlledTextInput
              error={errors.level}
              control={control}
              name="level"
              label="Level"
              type="number"
              disabled={isPending || isLevelDisabled}
              rules={{
                pattern: {
                  value: /^[0-9]+$/,
                  message: "Level must be a valid number"
                },
                min: {
                  value: 1,
                  message: "Level must be at least 1"
                },
                max: {
                  value: 500,
                  message: "Level cannot exceed 500"
                }
              }}
              helperText={
                isLevelDisabled ? "This field already has a value and cannot be modified" : "The player's current level (1-500)"
              }
              fullWidth
            />
            
            <ControlledSelect
              error={errors.platform}
              control={control}
              name="platform"
              label="Platform"
              disabled={isPending || isPlatformDisabled}
              options={platformOptions}
              rules={{
                pattern: {
                  value: /^[a-zA-Z0-9]+$/,
                  message: "Please select a valid platform"
                }
              }}
              helperText={
                isPlatformDisabled ? "This field already has a value and cannot be modified" : "Select the player's gaming platform"
              }
            />
            
            <ControlledTextInput
              error={errors.clan_tag}
              control={control}
              name="clan_tag"
              label="Clan Tag"
              disabled={isPending || isClanTagDisabled}
              rules={{
                pattern: {
                  value: /^[a-zA-Z0-9\s\-_\[\]]*$/,
                  message: "Clan tag can only contain letters, numbers, spaces, hyphens, underscores, and brackets"
                },
                maxLength: {
                  value: 4,
                  message: "Clan tag cannot exceed 4 characters"
                }
              }}
              helperText={
                errors.clan_tag ? errors.clan_tag.message : isClanTagDisabled ? "This field already has a value and cannot be modified" : "The player's clan tag (max 4 characters)"
              }
              fullWidth
            />

            <ControlledTextInput
              error={errors.eos_id}
              control={control}
              name="eos_id"
              label="EOS ID"
              disabled={isPending || isEosIdDisabled}
              helperText={
                isEosIdDisabled ? "This field already has a value and cannot be modified" : "The player's EOS ID"
              }
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={isPending}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            disabled={isPending || (isNameDisabled && isLevelDisabled && isPlatformDisabled && isClanTagDisabled)}
            startIcon={isPending ? <CircularProgress size={16} /> : null}
          >
            {isPending ? 'Updating...' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}

export default EditSoldierButton;