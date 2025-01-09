import Padlock from "@/components/shared/Padlock";
import SplitButton from "@/components/shared/SplitButton";
import { cmd } from "@/utils/fetchUtils";
import { parseVotekickThresholds } from "@/utils/lib";
import {
  Box,
  Slider,
  Stack,
  Typography,
  Grid2 as Grid,
  Input,
  Button,
  FormControl,
  InputLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Select,
  MenuItem,
  Divider,
  TextField,
  Alert,
} from "@mui/material";
import {Suspense, useState} from "react";
import { useLoaderData, defer, Await } from "react-router-dom";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import { ClientError } from "@/components/shared/ClientError";
import { useSettingsState } from "./useSettingsState";
import { AsyncClientError } from "@/components/shared/AsyncClientError";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { useInputHandlers } from "./useInputHandlers";
import { toast } from "react-toastify";

const INTENT = {
  SINGLE: 0,
  ALL: 1,
};

export const loader = async () => {
  const settingsPromise = cmd.GET_SERVER_SETTINGS().then((settings) => ({
    ...settings,
    votekick_thresholds: parseVotekickThresholds(settings.votekick_thresholds),
  }));
  const autoVotekickTogglePromise = cmd.GET_VOTEKICK_AUTOTOGGLE_CONFIG();
  const cameraNotificationsPromise = cmd.GET_CAMERA_NOTIFICATION_CONFIG();
  const realVipSlotsPromise = cmd.GET_REAL_VIP_CONFIG();
  const serverNamePromise = cmd.GET_SERVER_NAME();

  return defer({
    settings: settingsPromise,
    autoVotekickToggle: autoVotekickTogglePromise,
    cameraNotifications: cameraNotificationsPromise,
    realVipSlots: realVipSlotsPromise,
    serverName: serverNamePromise,
  });
};

export const action = async ({ request }) => {
  const data = await request.json();

  if (data.cmd === "set_server_settings") {
    const requests = Object.entries(data.settings).map(([key, value]) => {
      const payload = { forward: data.forward };
      let executeCommand;
      switch (key) {
        case "votekick_thresholds":
          payload.threshold_pairs = value;
          executeCommand = cmd.SET_VOTEKICK_THRESHOLDS;
          break;
        case "autobalance_enabled":
          payload.value = value;
          executeCommand = cmd.SET_AUTOBALANCE_ENABLED;
          break;
        case "votekick_enabled":
          payload.value = value;
          executeCommand = cmd.SET_VOTEKICK_ENABLED;
          break;
        case "team_switch_cooldown":
          payload.minutes = value;
          executeCommand = cmd.SET_TEAM_SWITCH_COOLDOWN;
          break;
        case "autobalance_threshold":
          payload.max_diff = value;
          executeCommand = cmd.SET_AUTOBALANCE_THRESHOLD;
          break;
        case "idle_autokick_time":
          payload.minutes = value;
          executeCommand = cmd.SET_IDLE_AUTOKICK_TIME;
          break;
        case "max_ping_autokick":
          payload.max_ms = value;
          executeCommand = cmd.SET_MAX_PING_AUTOKICK;
          break;
        case "queue_length":
          payload.value = value;
          executeCommand = cmd.SET_QUEUE_LENGTH;
          break;
        case "vip_slots_num":
          payload.value = value;
          executeCommand = cmd.SET_VIP_SLOTS_NUM;
          break;
        default:
          throw new ProgrammingError(`Trying to execute invalid command: ${key}`);
      }
      return executeCommand({ payload, throwRouteError: false });
    });

    try {
      await Promise.all(requests);
      return { success: true, cmd: "set_server_settings" };
    } catch (error) {
      return { success: false, error, cmd: "set_server_settings" };
    }
  }

  const { cmd: cmdName, ...payload } = data;
  let executeCommand;
  switch (cmdName) {
    case "set_server_name":
      executeCommand = cmd.SET_SERVER_NAME;
      break;
    case "set_camera_notification_config":
      executeCommand = cmd.SET_CAMERA_NOTIFICATION_CONFIG;
      break;
    case "set_auto_votekick_config":
      executeCommand = cmd.SET_VOTEKICK_AUTOTOGGLE_CONFIG;
      break;
    case "set_real_vip_config":
      executeCommand = cmd.SET_REAL_VIP_CONFIG;
      break;
  }

  try {
    await executeCommand({ payload, throwRouteError: false });
    return { success: true, cmd: cmdName };
  } catch (error) {
    return { success: false, error, cmd: cmdName };
  }
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

const GeneralSettingsContent = ({ settings }) => {
  const {
    pendingSettings,
    setPendingSettings,
    isSubmitting,
    error,
    submit,
    reset,
    isAltered,
  } = useSettingsState(settings);

  const {
    handleInputChange,
    handleBlur,
    handleSliderChange,
    handleToggleChange,
  } = useInputHandlers(pendingSettings, setPendingSettings);

  const submitChanges = (intent) => () => {
    const payload = {};
    payload.settings = Object.fromEntries(
      Object.entries(pendingSettings).filter(
        ([key, value]) =>
          JSON.stringify(settings[key]) !== JSON.stringify(value)
      )
    );
    payload.forward = intent === INTENT.ALL;
    payload.cmd = "set_server_settings";
    submit(payload, { method: "POST", encType: "application/json" });
  };

  const addThreshold = () => {
    const startingValue =
      pendingSettings.votekick_thresholds.length > 0
        ? pendingSettings.votekick_thresholds[
            pendingSettings.votekick_thresholds.length - 1
          ][0] + 1
        : 0;
    const newThreshold = [startingValue, 1];
    setPendingSettings((prev) => ({
      ...prev,
      votekick_thresholds: [...prev.votekick_thresholds, newThreshold],
    }));
  };

  const removeThreshold = (index) => {
    const updatedThresholds = pendingSettings.votekick_thresholds.filter(
      (_, i) => i !== index
    );

    setPendingSettings((prev) => ({
      ...prev,
      votekick_thresholds: updatedThresholds,
    }));
  };

  const handleThresholdChange = (index, keyIndex) => (event) => {
    const value = event.target.value === "" ? "" : Number(event.target.value);
    setPendingSettings((prev) => {
      const updatedThresholds = [...prev.votekick_thresholds];
      updatedThresholds[index][keyIndex] = value;
      return { ...prev, votekick_thresholds: updatedThresholds };
    });
  };

  const handleBlurThreshold = (index, keyIndex) => (event) => {
    const [min, max] = [event.target.min, event.target.max];
    setPendingSettings((prev) => {
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

  return (
    <Box>
      <Stack
        direction={"row"}
        sx={{ p: 1, mb: 1 }}
        justifyContent={"end"}
        alignItems={"center"}
        gap={1}
      >
        <Button disabled={!isAltered} variant="contained" onClick={reset}>
          Reset
        </Button>
        <SplitButton
          disabled={!isAltered}
          options={[
            {
              name: isSubmitting ? "Loading..." : "Apply",
              buttonProps: {
                onClick: submitChanges(INTENT.SINGLE),
                disabled: !isAltered,
              },
            },
            {
              name: isSubmitting ? "Loading..." : "Apply all servers",
              buttonProps: {
                onClick: submitChanges(INTENT.ALL),
                disabled: !isAltered,
              },
            },
          ]}
        />
      </Stack>
      {error && <ClientError error={error} />}
      <Stack gap={1}>
        <Box>
          <Typography variant="h6" id="autobalance-slider" gutterBottom>
            Autobalance{" "}
            {pendingSettings.autobalance_enabled ? "Enabled" : "Disabled"}
          </Typography>
          <Grid container spacing={4} sx={{ alignItems: "center" }}>
            <Grid size={{ xs: 10 }}>
              <Padlock
                label="Autobalance"
                checked={pendingSettings.autobalance_enabled}
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
            Votekick {pendingSettings.votekick_enabled ? "Enabled" : "Disabled"}
          </Typography>
          <Grid container spacing={4} sx={{ alignItems: "center" }}>
            <Grid size={{ xs: 10 }}>
              <Padlock
                label="Votekick"
                checked={pendingSettings.votekick_enabled}
                handleChange={handleToggleChange("votekick_enabled")}
              />
            </Grid>
          </Grid>
          <Typography variant="caption" color="text.secondary">
            Votekick will allow players to votekick players from the server.
          </Typography>
        </Box>
        {Object.entries(pendingSettings)
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
                    size="small"
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
          {pendingSettings.votekick_thresholds.map((threshold, index) => (
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
                          ? pendingSettings.votekick_thresholds[index - 1][0] +
                            1
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
          {!pendingSettings.votekick_thresholds.length && (
            <Typography
              component={"p"}
              variant="caption"
              color="text.secondary"
            >
              No thresholds set.
            </Typography>
          )}
          {(!pendingSettings.votekick_thresholds.length ||
            pendingSettings.votekick_thresholds[
              pendingSettings.votekick_thresholds.length - 1
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

const AutoVotekickContent = ({ settings }) => {
  const {
    pendingSettings,
    setPendingSettings,
    isSubmitting,
    error,
    submit,
    reset,
    isAltered,
  } = useSettingsState(settings);

  const { handleInputChange, handleBlur, handleToggleChange } =
    useInputHandlers(pendingSettings, setPendingSettings);

  const submitChanges = () => {
    const payload = {
      cmd: "set_auto_votekick_config",
      ...pendingSettings,
    };
    submit(payload, { method: "POST", encType: "application/json" });
  };

  return (
    <Box>
      <Stack
        direction={"row"}
        sx={{ p: 1, mb: 1 }}
        justifyContent={"end"}
        alignItems={"center"}
        gap={1}
      >
        <Padlock
          label="Auto Votekick Toggle"
          checked={pendingSettings.enabled}
          handleChange={handleToggleChange("enabled")}
        />
        <Box sx={{ flexGrow: 1 }} />
        <Button disabled={!isAltered} variant="contained" onClick={reset}>
          Reset
        </Button>
        <Button
          disabled={!isAltered}
          variant="contained"
          onClick={submitChanges}
        >
          {isSubmitting ? "Loading..." : "Apply"}
        </Button>
      </Stack>
      {error && <ClientError error={error} />}
      <Stack gap={1}>
        <Typography>
          When enabled, this feature manages the in-game votekicks by turning
          them off if the specified conditions are met, and turning them back on
          if they are not met. Ingame moderators are those who are actually
          playing the game on the server. Online moderators are those who are
          logged in CRCON's interface.
        </Typography>
        <Divider flexItem />
        <FormControl
          required
          error={pendingSettings.minimum_ingame_mods === ""}
          sx={{ mt: 2 }}
        >
          <InputLabel htmlFor={`in-game-moderators`}>
            Minimum in-game moderators
          </InputLabel>
          <Input
            id={`in-game-moderators`}
            value={pendingSettings.minimum_ingame_mods}
            onChange={handleInputChange("minimum_ingame_mods")}
            onBlur={handleBlur("minimum_ingame_mods")}
            placeholder="Minimum in-game moderators"
            type="number"
            inputProps={{
              min: 0,
            }}
          />
        </FormControl>
        <FormControl variant="standard" sx={{ mt: 2 }}>
          <InputLabel id="and-or-label">AND/OR</InputLabel>
          <Select
            labelId="and-or-label"
            value={pendingSettings.condition}
            onChange={(event) => {
              setPendingSettings((prev) => ({
                ...prev,
                condition: event.target.value,
              }));
            }}
          >
            <MenuItem value={"AND"}>AND</MenuItem>
            <MenuItem value={"OR"}>OR</MenuItem>
          </Select>
        </FormControl>
        <FormControl
          required
          error={pendingSettings.minimum_online_mods === ""}
          sx={{ mt: 2 }}
        >
          <InputLabel htmlFor={`online-crcon-moderators`}>
            Online CRCON moderators
          </InputLabel>
          <Input
            id={`online-crcon-moderators`}
            value={pendingSettings.minimum_online_mods}
            onChange={handleInputChange("minimum_online_mods")}
            onBlur={handleBlur("minimum_online_mods")}
            placeholder="Minimum online CRCON moderators"
            type="number"
            inputProps={{
              min: 0,
            }}
          />
        </FormControl>
      </Stack>
    </Box>
  );
};

const CameraNotificationsContent = ({ settings }) => {
  const {
    pendingSettings,
    setPendingSettings,
    isSubmitting,
    error,
    submit,
    reset,
    isAltered,
  } = useSettingsState(settings);

  const { handleToggleChange } = useInputHandlers(
    pendingSettings,
    setPendingSettings
  );

  const submitChanges = () => {
    const payload = {
      ...pendingSettings,
      cmd: "set_camera_notification_config",
    };
    submit(payload, { method: "POST", encType: "application/json" });
  };

  return (
    <Box>
      <Stack
        direction={"row"}
        sx={{ p: 1, mb: 1 }}
        justifyContent={"end"}
        alignItems={"center"}
        gap={1}
      >
        <Button disabled={!isAltered} variant="contained" onClick={reset}>
          Reset
        </Button>
        <Button
          disabled={!isAltered}
          variant="contained"
          onClick={submitChanges}
        >
          {isSubmitting ? "Loading..." : "Apply"}
        </Button>
      </Stack>
      {error && <ClientError error={error} />}
      <Stack gap={1}>
        <Typography>
          This feature will notify players whenever an admin enters Admin Camera
          mode (available only on PC servers as of version 15.2 of the game).
          You can choose to send a broadcast message or change the Welcome
          message. However, it is not recommended to change the Welcome message,
          as doing so will display the camera message first, followed by the
          default text a few seconds later. This will obscure the left side of
          all players' screens twice with each camera entrance.
        </Typography>
        <Divider flexItem />
        <Padlock
          label="Notify by Broadcast message"
          checked={pendingSettings.broadcast}
          handleChange={handleToggleChange("broadcast")}
        />
        <Padlock
          label="Notify by Welcome message"
          checked={pendingSettings.welcome}
          handleChange={handleToggleChange("welcome")}
        />
      </Stack>
    </Box>
  );
};

const RealVipSlotsContent = ({ settings }) => {
  const {
    pendingSettings,
    setPendingSettings,
    isSubmitting,
    error,
    submit,
    reset,
    isAltered,
  } = useSettingsState(settings);

  const { handleInputChange, handleBlur, handleToggleChange } =
    useInputHandlers(pendingSettings, setPendingSettings);

  const submitChanges = () => {
    const payload = {
      ...pendingSettings,
      cmd: "set_real_vip_config",
    };
    submit(payload, { method: "POST", encType: "application/json" });
  };

  return (
    <Box>
      <Stack
        direction={"row"}
        sx={{ p: 1, mb: 1 }}
        justifyContent={"end"}
        alignItems={"center"}
        gap={1}
      >
        <Padlock
          label="Real VIP Slots"
          checked={pendingSettings.enabled}
          handleChange={handleToggleChange("enabled")}
        />
        <Box sx={{ flexGrow: 1 }} />
        <Button disabled={!isAltered} variant="contained" onClick={reset}>
          Reset
        </Button>
        <Button
          disabled={!isAltered}
          variant="contained"
          onClick={submitChanges}
        >
          {isSubmitting ? "Loading..." : "Apply"}
        </Button>
      </Stack>
      {error && <ClientError error={error} />}
      <Stack gap={1}>
        <Typography>This is a legacy option that shouldn't be used.</Typography>
        <Typography>
          When enabled, each VIP that enters the server takes one VIP slot that
          is not released until the VIP leaves. This is achieved by dynamically
          setting the number of VIP slots based on the formula: (Max number of
          VIP slots - current number of VIPs in-game). The number of VIP slots
          will never fall below the "Min number of VIP slots". You can set this
          minimum to 0 to create a hard cap. If you use the autoSettings, ensure
          that you do not set the VIPs in there, as it will override the realVIP
          system.
        </Typography>
        <Divider flexItem />
        <FormControl
          required
          error={pendingSettings.minimum_number_vip_slots === ""}
          sx={{ mt: 2 }}
        >
          <InputLabel htmlFor={`minimum-vip-slots`}>
            Minimum VIP slots
          </InputLabel>
          <Input
            id={`minimum-vip-slots`}
            value={pendingSettings.minimum_number_vip_slots}
            onChange={handleInputChange("minimum_number_vip_slots")}
            onBlur={handleBlur("minimum_number_vip_slots")}
            placeholder="Minimum VIP slots"
            type="number"
            inputProps={{
              min: 0,
            }}
          />
        </FormControl>
        <FormControl
          required
          error={pendingSettings.desired_total_number_vips === ""}
          sx={{ mt: 2 }}
        >
          <InputLabel htmlFor={`max-vip-slots`}>Max VIP slots</InputLabel>
          <Input
            id={`max-vip-slots`}
            value={pendingSettings.desired_total_number_vips}
            onChange={handleInputChange("desired_total_number_vips")}
            onBlur={handleBlur("desired_total_number_vips")}
            placeholder="Max VIP slots"
            type="number"
            inputProps={{
              min: 0,
            }}
          />
        </FormControl>
      </Stack>
    </Box>
  );
};

const ServerNameContent = ({ settings }) => {
  const {
    pendingSettings: pendingServerNameSettings,
    setPendingSettings: setPendingServerNameSettings,
    isSubmitting,
    error,
    submit,
    reset,
    isAltered,
  } = useSettingsState(settings);

  const submitChanges = () => {
    const payload = { name: pendingServerNameSettings, cmd: "set_server_name" };
    submit(payload, { method: "POST", encType: "application/json" });
  };

  return (
    <Box>
      <Stack
        direction={"row"}
        sx={{ p: 1, mb: 1 }}
        justifyContent={"end"}
        alignItems={"center"}
        gap={1}
      >
        <Button disabled={!isAltered} variant="contained" onClick={reset}>
          Reset
        </Button>
        <Button
          disabled={!isAltered}
          variant="contained"
          onClick={submitChanges}
        >
          {isSubmitting ? "Loading..." : "Apply"}
        </Button>
      </Stack>
      {error && <ClientError error={error} />}
      <Stack gap={1}>
        <Typography>
          If your game server is hosted on GTX (maybe on others [to be
          confirmed], as long as they allow SFTP access to your files), you can
          change the server's name without restarting it. You'll first have to
          set : the SFTP credentials in your .env file (refer to the
          installation procedure) ; the game server IP and SFTP port in the GTX
          Server Name Change settings. Note the new name will only be visible
          after a map change.
        </Typography>
        <Divider flexItem />
        <TextField
          label="Server Name"
          value={pendingServerNameSettings}
          onChange={(event) => {
            // Workaround to set the value as a string because
            // this settings is a single string not an object
            // with a key "server_name"
            setPendingServerNameSettings(event.target.value);
          }}
          sx={{ mt: 2 }}
        />
      </Stack>
    </Box>
  );
};

const PANEL_TITLES = {
  settings: "General Settings",
  autoVotekickToggle: "Auto Votekick",
  cameraNotifications: "Camera Notifications",
  realVipSlots: "Real VIP Slots",
  serverName: "Server Name",
};

const PANEL_COMPONENTS = {
  settings: GeneralSettingsContent,
  autoVotekickToggle: AutoVotekickContent,
  cameraNotifications: CameraNotificationsContent,
  realVipSlots: RealVipSlotsContent,
  serverName: ServerNameContent,
};

const SettingsPage = () => {
  const data = useLoaderData();
  const [expanded, setExpanded] = useState(false);
  const [isFlushingCache, setIsFlushingCache] = useState(false);
  const [isReconnectingToGameserver, setIsReconnectingToGameserver] = useState(false);

  const handleChange = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : false);
  };

  return (
    <Box sx={{ maxWidth: (theme) => theme.breakpoints.values.md }}>
      {Object.keys(data).map((key, index) => (
        <Accordion
          key={key}
          expanded={expanded === `panel${index}`}
          onChange={handleChange(`panel${index}`)}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls={`panel${index}bh-content`}
            id={`panel${index}bh-header`}
          >
            <Typography sx={{ width: "33%", flexShrink: 0 }}>
              {PANEL_TITLES[key]}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Suspense fallback={<div>Loading settings...</div>}>
              <Await
                resolve={data[key]}
                errorElement={<AsyncClientError title={PANEL_TITLES[key]} />}
              >
                {(resolvedSettings) => {
                  const Component = PANEL_COMPONENTS[key];
                  return <Component settings={resolvedSettings} />;
                }}
              </Await>
            </Suspense>
          </AccordionDetails>
        </Accordion>
      ))}
      <Accordion
        key="actions"
        expanded={expanded === "actions"}
        onChange={handleChange("actions")}
      >
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls={`actions-bh-content`}
          id={`actions-bh-header`}
        >
          <Typography sx={{ width: "33%", flexShrink: 0 }}>
            CRCON Actions
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Alert severity="warning">
            Do not use this until instructed to do so by the CRCON maintainers.
          </Alert>
          <Typography variant="h6">Clear Application Cache</Typography>
          <Typography>
            Clicking on this will flush the internal cache used by different
            CRCON components. Avoid using it unnecessarily, as it forces a lot
            of data to be recalculated and reloaded.
          </Typography>
          <Button
            disabled={isFlushingCache}
            variant="contained"
            onClick={async () => {
              setIsFlushingCache(true);
              try {
                await cmd.CLEAR_APPLICATION_CACHE({ throwRouteError: false });
                toast.success("Cache flushed successfully");
              } catch (error) {
                toast.error(error.message ?? "Failed to flush cache");
              } finally {
                setIsFlushingCache(false);
              }
            }}
          >
            {isFlushingCache ? "Flushing..." : "Flush Cache"}
          </Button>
          <Typography variant="h6">Reconnect to gameserver</Typography>
          <Button
            disabled={isReconnectingToGameserver}
            variant="contained"
            onClick={async () => {
              setIsReconnectingToGameserver(true);
              try {
                await cmd.RECONNECT_GAME_SERVER({ throwRouteError: false });
                toast.success("Reconnected to gameserver successfully");
              } catch (error) {
                toast.error(
                  error.message ?? "Failed to reconnect to gameserver"
                );
              } finally {
                setIsReconnectingToGameserver(false);
              }
            }}
          >
            {isReconnectingToGameserver ? "Reconnecting..." : "Reconnect"}
          </Button>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default SettingsPage;
