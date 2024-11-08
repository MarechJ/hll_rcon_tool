import Padlock from "@/components/shared/Padlock";
import SplitButton from "@/components/shared/SplitButton";
import { cmd } from "@/utils/fetchUtils";
import { parseVotekickThresholds } from "@/utils/lib";
import {
  Box,
  Paper,
  Slider,
  Stack,
  Typography,
  Grid2 as Grid,
  Input,
  Button,
  FormControl,
  InputLabel,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { useActionData, useLoaderData, useSubmit } from "react-router-dom";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import { ClientError } from "@/components/shared/ClientError";

const INTENT = {
  SINGLE: 0,
  ALL: 1,
};

export const loader = async () => {
  const settings = await cmd.GET_SERVER_SETTINGS();
  return {
    settings: {
      ...settings,
      votekick_thresholds: parseVotekickThresholds(
        settings.votekick_thresholds
      ),
    },
  };
};

export const action = async ({ request }) => {
  const { settings, forward } = await request.json();
  const requests = Object.entries(settings).map(([key, value]) => {
    const payload = { forward };
    let command;
    switch (key) {
      case "votekick_thresholds":
        payload.threshold_pairs = value;
        command = cmd.SET_VOTEKICK_THRESHOLDS;
        break;
      case "autobalance_enabled":
        payload.value = value;
        command = cmd.SET_AUTOBALANCE_ENABLED;
        break;
      case "votekick_enabled":
        payload.value = value;
        command = cmd.SET_VOTEKICK_ENABLED;
        break;
      case "team_switch_cooldown":
        payload.minutes = value;
        command = cmd.SET_TEAM_SWITCH_COOLDOWN;
        break;
      case "autobalance_threshold":
        payload.max_diff = value;
        command = cmd.SET_AUTOBALANCE_THRESHOLD;
        break;
      case "idle_autokick_time":
        payload.minutes = value;
        command = cmd.SET_IDLE_AUTOKICK_TIME;
        break;
      case "max_ping_autokick":
        payload.max_ms = value;
        command = cmd.SET_MAX_PING_AUTOKICK;
        break;
      case "queue_length":
        payload.value = value;
        command = cmd.SET_QUEUE_LENGTH;
        break;
      case "vip_slots_num":
        payload.value = value;
        command = cmd.SET_VIP_SLOTS_NUM;
        break;
    }
    return command({ payload, throwRouteError: false });
  });

  try {
    await Promise.all(requests);
    return { success: true };
  } catch (error) {
    return { success: false, error };
  }
};

const SettingsPage = () => {
  const { settings } = useLoaderData();
  const [localSettings, setLocalSettings] = useState(settings);
  const submit = useSubmit();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const actionData = useActionData();
  const [error, setError] = useState(null);

  const submitChanges = (intent) => () => {
    setIsSubmitting(true);
    const payload = {};
    // include only settings attributes that are different from the original settings  
    // to avoid unnecessary updates
    payload.settings = Object.fromEntries(
      Object.entries(localSettings).filter(
        ([key, value]) => JSON.stringify(settings[key]) !== JSON.stringify(value)
      )
    );
    payload.forward = intent === INTENT.ALL;
    submit(payload, { method: "POST", encType: "application/json" });
  };

  const handleInputChange = (key) => (event) => {
    const value = event.target.value === "" ? "" : Number(event.target.value);
    setLocalSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleSliderChange = (key) => (event, value) => {
    setLocalSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleToggleChange = (key) => (checked) => {
    setLocalSettings((prev) => ({ ...prev, [key]: checked }));
  };

  const handleBlur = (key) => () => {
    if (localSettings[key] < 0) {
      setLocalSettings((prev) => ({ ...prev, [key]: 0 }));
    } else if (localSettings[key] > getMaxValue(key)) {
      setLocalSettings((prev) => ({ ...prev, [key]: getMaxValue(key) }));
    }
  };

  const handleReset = () => {
    setLocalSettings(settings);
  };

  const addThreshold = () => {
    const startingValue =
      localSettings.votekick_thresholds.length > 0
        ? localSettings.votekick_thresholds[
            localSettings.votekick_thresholds.length - 1
          ][0] + 1
        : 0;
    const newThreshold = [startingValue, 1];
    setLocalSettings((prev) => ({
      ...prev,
      votekick_thresholds: [...prev.votekick_thresholds, newThreshold],
    }));
  };

  const removeThreshold = (index) => {
    const updatedThresholds = localSettings.votekick_thresholds.filter(
      (_, i) => i !== index
    );

    setLocalSettings((prev) => ({
      ...prev,
      votekick_thresholds: updatedThresholds,
    }));
  };

  const handleThresholdChange = (index, keyIndex) => (event) => {
    const value = event.target.value === "" ? "" : Number(event.target.value);
    setLocalSettings((prev) => {
      const updatedThresholds = [...prev.votekick_thresholds];
      updatedThresholds[index][keyIndex] = value;
      return { ...prev, votekick_thresholds: updatedThresholds };
    });
  };

  const handleBlurThreshold = (index, keyIndex) => (event) => {
    const [min, max] = [event.target.min, event.target.max];
    setLocalSettings((prev) => {
      const updatedThresholds = [...prev.votekick_thresholds];
      const threshold = updatedThresholds[index][keyIndex];
      if (threshold < min) {
        updatedThresholds[index][keyIndex] = min;
      } else if (threshold > max) {
        updatedThresholds[index][keyIndex] = max;
      }
      return { ...prev, votekick_thresholds: updatedThresholds };
    });
  };

  const settingsHasChanged = useMemo(() => {
    if (isSubmitting) return false;
    for (const key in settings) {
      if (settings[key] !== localSettings[key]) {
        return true;
      }
    }
    return false;
  }, [settings, localSettings, isSubmitting]);

  useEffect(() => {
    if (actionData && settings) {
      if (actionData.success) {
        setError(null);
        setLocalSettings(settings);
      } else {
        setError(actionData.error);
      }
      setIsSubmitting(false);
    }
  }, [actionData, settings]);

  return (
    <Box
      sx={{
        maxWidth: (theme) => theme.breakpoints.values.md,
      }}
    >
      <Stack
        component={Paper}
        direction={"row"}
        sx={{ p: 1, mb: 1 }}
        justifyContent={"end"}
        alignItems={"center"}
        gap={1}
      >
        <Button
          disabled={!settingsHasChanged}
          variant="contained"
          onClick={handleReset}
        >
          Reset
        </Button>
        <SplitButton
          disabled={!settingsHasChanged}
          options={[
            {
              name: isSubmitting ? "Loading..." : "Apply",
              buttonProps: {
                onClick: submitChanges(INTENT.SINGLE),
                disabled: !settingsHasChanged,
              },
            },
            {
              name: isSubmitting ? "Loading..." : "Apply all servers",
              buttonProps: {
                onClick: submitChanges(INTENT.ALL),
                disabled: !settingsHasChanged,
              },
            },
          ]}
        />
      </Stack>
      {error && (
        <ClientError error={error} />
      )}
      <Stack spacing={4}>
        <Box>
          <Typography variant="h6" id="autobalance-slider" gutterBottom>
            Autobalance{" "}
            {localSettings.autobalance_enabled ? "Enabled" : "Disabled"}
          </Typography>
          <Grid container spacing={4} sx={{ alignItems: "center" }}>
            <Grid size={{ xs: 10 }}>
              <Padlock
                label="Autobalance"
                checked={localSettings.autobalance_enabled}
                handleChange={handleToggleChange("autobalance_enabled")}
              />
            </Grid>
          </Grid>
          <Typography variant="caption" color="text.secondary">
            Autobalance will automatically move players around to balance the
            teams.
          </Typography>
        </Box>
        <Box>
          <Typography variant="h6" id="votekick-slider" gutterBottom>
            Votekick {localSettings.votekick_enabled ? "Enabled" : "Disabled"}
          </Typography>
          <Grid container spacing={4} sx={{ alignItems: "center" }}>
            <Grid size={{ xs: 10 }}>
              <Padlock
                label="Votekick"
                checked={localSettings.votekick_enabled}
                handleChange={handleToggleChange("votekick_enabled")}
              />
            </Grid>
          </Grid>
          <Typography variant="caption" color="text.secondary">
            Votekick will allow players to votekick players from the server.
          </Typography>
        </Box>
        {Object.entries(localSettings)
          .filter(
            ([key]) =>
              ![
                "autobalance_enabled",
                "votekick_enabled",
                "votekick_thresholds",
              ].includes(key)
          )
          .map(([key, value]) => (
            <Box key={key} sx={{ width: "100%" }}>
              <Typography variant="h6" id={`${key}-slider`} gutterBottom>
                {/* Capitalize the first letter of each word */}
                {key
                  .replace(/_/g, " ")
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </Typography>
              <Grid container spacing={4} sx={{ alignItems: "center" }}>
                <Grid size={{ xs: 10 }}>
                  <Slider
                    value={typeof value === "number" ? value : 0}
                    onChange={handleSliderChange(key)}
                    aria-labelledby={`${key}-slider`}
                    max={getMaxValue(key)}
                    marks={getMarks(key)}
                    step={getStep(key)}
                    valueLabelDisplay="auto"
                  />
                </Grid>
                <Grid size={{ xs: 2 }}>
                  <Input
                    value={value}
                    size="small"
                    onChange={handleInputChange(key)}
                    onBlur={handleBlur(key)}
                    inputProps={{
                      step: getStep(key),
                      min: 0,
                      max: getMaxValue(key),
                      type: "number",
                      "aria-labelledby": `${key}-slider`,
                    }}
                  />
                </Grid>
              </Grid>
              <Typography variant="caption" color="text.secondary">
                {getHelpText(key)}
              </Typography>
            </Box>
          ))}
        <Box sx={{ width: "100%" }}>
          <Typography variant="h6" id="votekick-thresholds" gutterBottom>
            Votekick Thresholds
          </Typography>
          {localSettings.votekick_thresholds.map((threshold, index) => (
            <Grid
              container
              spacing={2}
              key={`threshold-${index}`}
              sx={{ mb: 2, alignItems: "center" }}
            >
              <Grid size={8}>
                <FormControl fullWidth size="small">
                  <InputLabel htmlFor={`threshold-${index}-min`}>
                    Min. players
                  </InputLabel>
                  <Input
                    id={`threshold-${index}-min`}
                    value={threshold[0]}
                    onChange={handleThresholdChange(index, 0)}
                    onBlur={handleBlurThreshold(index, 0)}
                    placeholder="Min. players"
                    readOnly={index === 0}
                    type="number"
                    inputProps={{
                      min:
                        index > 0
                          ? localSettings.votekick_thresholds[index - 1][0] + 1
                          : 0,
                      max: getMaxValue("players"),
                    }}
                    size="small"
                  />
                </FormControl>
              </Grid>
              <Grid size={2}>
                <FormControl fullWidth size="small">
                  <InputLabel htmlFor={`threshold-${index}-votes`}>
                    Votes
                  </InputLabel>
                  <Input
                    id={`threshold-${index}-votes`}
                    value={threshold[1]}
                    onChange={handleThresholdChange(index, 1)}
                    onBlur={handleBlurThreshold(index, 1)}
                    placeholder="Votes"
                    type="number"
                    inputProps={{
                      min: 1,
                      max: getMaxValue("players"),
                    }}
                    size="small"
                  />
                </FormControl>
              </Grid>
              <Grid size={2}>
                <Button
                  size="small"
                  onClick={() => removeThreshold(index)}
                  sx={{ minWidth: "auto" }}
                >
                  <DeleteIcon />
                </Button>
              </Grid>
            </Grid>
          ))}
          {!localSettings.votekick_thresholds.length && (
            <Typography
              component={"p"}
              variant="caption"
              color="text.secondary"
            >
              No thresholds set.
            </Typography>
          )}
          {(!localSettings.votekick_thresholds.length ||
            localSettings.votekick_thresholds[
              localSettings.votekick_thresholds.length - 1
            ][0] < 50) && (
            <Button
              startIcon={<AddIcon />}
              onClick={addThreshold}
              variant="outlined"
              size="small"
            >
              Add Threshold
            </Button>
          )}
          <Typography component={"p"} variant="caption" color="text.secondary">
            Set the number of votes required to kick a player based on the
            number of players in the team. The first field defines the minimum
            number of players in the team, and the second field defines the
            number of votes required. Reasonable values are [0, 1], [10, 5],
            [25, 12], [50, 20].
          </Typography>
        </Box>
      </Stack>
    </Box>
  );
};

// Helper functions
const getMaxValue = (key) => {
  switch (key) {
    case "team_switch_cooldown":
      return 30;
    case "idle_autokick_time":
      return 200;
    case "max_ping_autokick":
      return 2000;
    case "queue_length":
      return 6;
    case "vip_slots_num":
      return 100;
    case "players":
    case "autobalance_threshold":
      return 50;
    default:
      return 100; // Default max value
  }
};

const getMarks = (key) => {
  switch (key) {
    case "team_switch_cooldown":
      return [0, 5, 10, 15, 20, 25, 30].map((val) => ({
        value: val,
        label: `${val}`,
      }));
    case "idle_autokick_time":
      return [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200].map((val) => ({
        value: val,
        label: `${val}`,
      }));
    case "max_ping_autokick":
      return [0, 500, 1000, 1500, 2000].map((val) => ({
        value: val,
        label: `${val}`,
      }));
    case "queue_length":
      return [0, 1, 2, 3, 4, 5, 6].map((val) => ({
        value: val,
        label: `${val}`,
      }));
    case "vip_slots_num":
      return [0, 20, 40, 60, 80, 100].map((val) => ({
        value: val,
        label: `${val}`,
      }));
    default:
      return [];
  }
};

const getHelpText = (key) => {
  switch (key) {
    case "autobalance_threshold":
      return "0 means the teams must match exactly";
    case "max_queue_length":
      return "Maximum # of people waiting";
    case "vip_slots_num":
      return "# slots reserved for VIPs";
    default:
      return "0 to disable";
  }
};

const getStep = (key) => {
  switch (key) {
    case "team_switch_cooldown":
      return 1;
    case "idle_autokick_time":
    case "max_ping_autokick":
      return 10;
    case "queue_length":
    case "vip_slots_num":
      return 1;
    default:
      return 1;
  }
};

export default SettingsPage;
