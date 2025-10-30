import React from "react";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Chip from "@mui/material/Chip";
import { Stack, Alert, CircularProgress, FormControlLabel, Switch, Autocomplete } from "@mui/material";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { cmd } from "@/utils/fetchUtils";
import CheckIcon from "@mui/icons-material/Check";
import ErrorIcon from "@mui/icons-material/Error";
import { ControlledTextInput } from "@/components/form/core/ControlledTextInput";
import { ControlledSelect } from "@/components/form/core/ControlledSelect";
import countries from "country-list";
import { CountryFlag } from "@/components/shared/CountryFlag";
import ISO6391 from 'iso-639-1';

// Get all countries for autocomplete
const countryOptions = countries.getCodes().map((code) => ({
  code: code.toLowerCase(),
  name: countries.getName(code),
}));

// Get all languages for autocomplete
const languageOptions = ISO6391.getLanguages(ISO6391.getAllCodes()).map((lang) => ({
  code: lang.code,
  name: lang.name,
}));

function EditAccountButton({ Icon, playerId, currentAccountData }) {
  const [open, setOpen] = React.useState(false);
  const [submitStatus, setSubmitStatus] = React.useState(null); // null, 'success', 'error'
  const [errorMessage, setErrorMessage] = React.useState("");
  const [selectedCountry, setSelectedCountry] = React.useState(
    currentAccountData?.country || ""
  );
  const queryClient = useQueryClient();

  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
    ...formProps
  } = useForm({
    defaultValues: {
      name: currentAccountData?.name || "",
      discord_id: currentAccountData?.discord_id || "",
      is_member: currentAccountData?.is_member || false,
      country: currentAccountData?.country || "",
      lang: currentAccountData?.lang || "en",
    },
  });

  // Watch the country field to sync with local state
  const watchedCountry = watch("country");
  React.useEffect(() => {
    setSelectedCountry(watchedCountry || "");
  }, [watchedCountry]);

  const { mutate: editPlayerAccount, isPending } = useMutation({
    mutationFn: async (data) => {
      // Convert empty strings to null and ensure proper types
      const payload = {
        player_id: playerId,
        name: data.name || null,
        discord_id: data.discord_id || null,
        is_member: Boolean(data.is_member),
        country: data.country || null,
        lang: data.lang || "en",
      };
      
      return cmd.EDIT_PLAYER_ACCOUNT({
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
      setErrorMessage(error.message || 'Failed to update player account information');
    },
  });

  const handleClickOpen = () => {
    setOpen(true);
    setSubmitStatus(null);
    setErrorMessage("");
    // Reset form with current values
    const currentValues = {
      name: currentAccountData?.name || "",
      discord_id: currentAccountData?.discord_id || "",
      is_member: currentAccountData?.is_member || false,
      country: currentAccountData?.country || "",
      lang: currentAccountData?.lang || "en",
    };
    reset(currentValues);
    setSelectedCountry(currentValues.country);
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
    editPlayerAccount(data);
  };

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
        <DialogTitle>Edit Player Account Information</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Update the player's account information. All fields can be modified.
          </DialogContentText>
          
          {submitStatus === 'success' && (
            <Alert severity="success" sx={{ mt: 2 }}>
              <CheckIcon sx={{ mr: 1 }} />
              Successfully updated account information!
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
              control={control}
              name="name"
              label="Account Name"
              rules={{
                pattern: {
                  value: /^[a-zA-Z0-9\s\-_]+$/,
                  message: "Name can only contain letters, numbers, spaces, hyphens, and underscores"
                }
              }}
              helperText="The player's account name"
              fullWidth
            />
            
            <ControlledTextInput
              control={control}
              name="discord_id"
              label="Discord ID"
              rules={{
                pattern: {
                  value: /^\d+$/,
                  message: "Discord ID must be a valid number"
                }
              }}
              helperText="The player's Discord user ID (numeric)"
              fullWidth
            />

            <FormControlLabel
              control={
                <Switch
                  checked={watch("is_member")}
                  onChange={(e) => setValue("is_member", e.target.checked)}
                  disabled={isPending}
                />
              }
              label="Is Member"
            />

            <Autocomplete
              options={countryOptions}
              getOptionLabel={(option) => option.name}
              value={countryOptions.find((c) => c.code === selectedCountry) || null}
              onChange={(event, newValue) => {
                setSelectedCountry(newValue?.code || "");
                setValue("country", newValue?.code || "", { shouldValidate: true });
              }}
              disabled={isPending}
              renderOption={({ key, ...props }, option) => (
                <li key={key} {...props}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <CountryFlag country={option.code} />
                    <span>{option.name}</span>
                  </Stack>
                </li>
              )}
              renderInput={(params) => (
                <ControlledTextInput
                  {...params}
                  control={control}
                  name="country"
                  label="Country"
                  rules={{
                    pattern: {
                      value: /^[a-z]{2}$|^$/,
                      message: "Country must be a valid 2-letter ISO code"
                    }
                  }}
                  helperText="Select the player's country"
                  fullWidth
                />
              )}
            />

            <Autocomplete
              options={languageOptions}
              getOptionLabel={(option) => option.name}
              value={languageOptions.find((l) => l.code === watch("lang")) || null}
              onChange={(event, newValue) => {
                setValue("lang", newValue?.code || "", { shouldValidate: true });
              }}
              disabled={isPending}
              renderInput={(params) => (
                <ControlledTextInput
                  {...params}
                  control={control}
                  name="lang"
                  label="Language"
                  rules={{
                    pattern: {
                      value: /^[a-z]{2}$/,
                      message: "Language must be a valid 2-letter ISO code"
                    }
                  }}
                  helperText="Select the player's preferred language"
                  fullWidth
                />
              )}
            />  
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={isPending}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            disabled={isPending}
            startIcon={isPending ? <CircularProgress size={16} /> : null}
          >
            {isPending ? 'Updating...' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}

export default EditAccountButton;