import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useLoaderData } from "react-router-dom";
import {
  mapsManagerMutationOptions,
  mapsManagerQueryKeys,
  mapsManagerQueryOptions,
} from "../../queries";
import { useEffect, useRef, useState } from "react";
import _ from "lodash";
import { toast } from "react-toastify";
import { VotemapChangeNotification } from "./VotemapChangeNotification";
import {
  Button,
  CircularProgress,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import {
  defaultMapOptions,
  messageFieldConfigs,
  padlockConfigs,
  textFieldConfigs,
} from "./configs-data";
import Padlock from "@/components/shared/Padlock";
import SaveIcon from "@mui/icons-material/Save";
import ReplayIcon from "@mui/icons-material/Replay";
import { lazy, Suspense } from "react";
const EmojiPicker = lazy(() => import("@emoji-mart/react"));
import emojiData from "@emoji-mart/data/sets/15/twitter.json";
import DeleteIcon from "@mui/icons-material/Delete";
import Emoji from "@/components/shared/Emoji";

function VotemapSettingsPage() {
  const loaderData = useLoaderData();
  const queryClient = useQueryClient();

  const { data: config } = useQuery({
    ...mapsManagerQueryOptions.voteMapConfig(),
    initialData: loaderData.config,
    refetchInterval: 5_000,
    staleTime: 5_000,
    refetchOnMount: false,
  });

  const { mutate: changeConfig, isPending: isConfigSaving } = useMutation({
    ...mapsManagerMutationOptions.setVotemapConfig,
    onSuccess: () => {
      // Update this reference so the user does not get change
      // notification about his own changes
      prevConfig.current = workingConfig;
      queryClient.invalidateQueries([
        mapsManagerQueryKeys.voteMapConfig,
        mapsManagerQueryKeys.votemapStatus,
      ]);
      toast.success(`Votemap config has been changed`);
    },
    onError: (error) => {
      toast.error(
        <div>
          <span>{error.name}</span>
          <p>{error.message}</p>
        </div>
      );
    },
  });

  const prevConfig = useRef(config);
  const [workingConfig, setWorkingConfig] = useState(config);
  const [emojiPickerOpen, setEmojiPickerOpen] = useState(false);
  const [emojiPickerIndex, setEmojiPickerIndex] = useState(null);

  // Compare incoming config changes
  const handleIncomingConfigChange = () => {
    // check how the configs differ (deep comparison)
    const diff = _.transform(
      prevConfig.current,
      (result, value, key) => {
        if (!_.isEqual(value, config[key])) {
          result.push(key);
        }
      },
      []
    );

    // no changes do nothing
    const numberOfChanges = diff.length;
    if (numberOfChanges === 0) return;

    const enabledOnly = numberOfChanges === 1 && diff.includes("enabled");

    // update reference
    // this will also prevent infinite toasting for the same changes
    prevConfig.current = _.cloneDeep(config);

    // if only 'enabled' changed do nothing
    if (enabledOnly) return;

    // announce there have been some changes made
    toast(VotemapChangeNotification, {
      onClose(reason) {
        // No-op: all logic is handled in the onAccept callback below
      },
      data: {
        changes: diff,
        onAccept: () => {
          setWorkingConfig((prev) => {
            const combined = { ...prev };
            diff.forEach((key) => {
              combined[key] = _.cloneDeep(config[key]);
            });
            return combined;
          });
        },
      },
      autoClose: false,
      closeOnClick: false,
    });
  };

  const handleConfigReset = () => {
    setWorkingConfig(prevConfig.current);
  };

  const handleConfigSave = () => {
    changeConfig(workingConfig);
  };

  const handleWorkingChanges = (propName) => (value) => {
    // When Event object is being passed in as a value
    if (typeof value === "object" && "target" in value) {
      const isNumber = value.target.type === "number";
      value = isNumber ? Number(value.target.value) : value.target.value;
    }
    setWorkingConfig((prevConfig) => ({
      ...prevConfig,
      [propName]: value,
    }));
  };

  // vote_flags handlers
  const handleAddVoteFlag = () => {
    setWorkingConfig((prev) => ({
      ...prev,
      vote_flags: [
        ...(prev.vote_flags || []),
        { flag: "", vote_count: 0 },
      ],
    }));
  };

  const handleRemoveVoteFlag = (index) => {
    setWorkingConfig((prev) => ({
      ...prev,
      vote_flags: prev.vote_flags.filter((_, i) => i !== index),
    }));
  };

  const handleVoteFlagChange = (index, key, value) => {
    setWorkingConfig((prev) => {
      const updated = [...(prev.vote_flags || [])];
      if (key === "vote_count") {
        value = Math.max(0, Math.min(100, Number(value)));
      }
      updated[index] = { ...updated[index], [key]: value };
      return { ...prev, vote_flags: updated };
    });
  };

  const handleOpenEmojiPicker = (index) => {
    setEmojiPickerIndex(index);
    setEmojiPickerOpen(true);
  };

  const handleCloseEmojiPicker = () => {
    setEmojiPickerOpen(false);
    setEmojiPickerIndex(null);
  };

  const handleEmojiSelected = (emoji) => {
    if (emojiPickerIndex !== null) {
      handleVoteFlagChange(emojiPickerIndex, "flag", emoji.native);
    }
    handleCloseEmojiPicker();
  };

  useEffect(handleIncomingConfigChange, [config, workingConfig]);

  return (
    <Stack
      component={"section"}
      direction={{ xs: "column", md: "row" }}
      spacing={1}
    >
      {/* TOP/LEFT SIDE */}
      <Stack sx={{ width: { xs: "100%", md: "50%" } }} spacing={1}>
        <Typography variant="h6">Messages</Typography>
        {messageFieldConfigs.map((configItem) => (
          <TextField
            key={configItem.name}
            fullWidth
            variant="filled"
            multiline
            rows={configItem.rows}
            label={configItem.label}
            helperText={configItem.helperText}
            value={workingConfig[configItem.name] ?? ""}
            onChange={handleWorkingChanges(configItem.name)}
          />
        ))}
      </Stack>
      <Divider flexItem orientation={"vertical"} />
      {/* BOTTOM/RIGHT SIDE */}
      <Stack
        direction={{ xs: "column-reverse", md: "column" }}
        sx={{ width: { xs: "100%", md: "50%" } }}
        spacing={1}
      >
        {/* Actions */}
        <Stack
          direction="row"
          spacing={1}
          justifyContent={"end"}
          alignItems={"center"}
          sx={{
            height: 50,
            p: 1,
            border: (theme) => `1px solid ${theme.palette.divider}`,
          }}
        >
          <Button
            color="warning"
            variant="outlined"
            onClick={handleConfigReset}
            startIcon={<ReplayIcon />}
          >
            Reset
          </Button>
          <Button
            variant="contained"
            color="primary"
            disabled={false}
            onClick={handleConfigSave}
            startIcon={
              isConfigSaving ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <SaveIcon />
              )
            }
          >
            Save
          </Button>
        </Stack>
        {/* Form fields */}
        <Stack spacing={1}>
          <Typography variant="h6">Configuration</Typography>
          <FormControl>
            <InputLabel id="default_method">
              Default map method (when no votes)
            </InputLabel>
            <Select
              value={workingConfig.default_method ?? ""}
              onChange={handleWorkingChanges("default_method")}
              label={"Default map method (when no votes)"}
              labelId="default_method"
            >
              {defaultMapOptions.map((option) => (
                <MenuItem key={option.name} value={option.name}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Divider flexItem orientation={"horizontal"} />

          {padlockConfigs.map(({ name, label }) => (
            <Padlock
              key={name}
              label={label}
              checked={workingConfig[name] ?? false}
              handleChange={handleWorkingChanges(name)}
            />
          ))}

          <Divider flexItem orientation={"horizontal"} />

          {textFieldConfigs.map((configItem) => (
            <TextField
              key={configItem.name}
              variant="filled"
              fullWidth
              type="number"
              slotProps={{
                input: configItem.inputProps,
              }}
              label={configItem.label}
              helperText={configItem.helperText}
              value={workingConfig[configItem.name] ?? false}
              onChange={handleWorkingChanges(configItem.name)}
            />
          ))}

          <Divider flexItem orientation={"horizontal"} />
          
          {/* Vote Flags Section */}
          <Typography variant="subtitle1">Vote Flags</Typography>
          <Stack spacing={1}>
            {(workingConfig.vote_flags || []).map((item, idx) => (
              <Stack key={idx} direction="row" spacing={1} alignItems="center">
                <Button
                  variant="outlined"
                  onClick={() => handleOpenEmojiPicker(idx)}
                  sx={{ minWidth: 48, fontSize: 24 }}
                >
                  <Emoji emoji={item.flag || "❓"} />
                </Button>
                <TextField
                  type="number"
                  label="Vote Count"
                  slotProps={{ input: { min: 0, max: 100 } }}
                  value={item.vote_count}
                  onChange={(e) => handleVoteFlagChange(idx, "vote_count", e.target.value)}
                  sx={{ width: 120 }}
                />
                <Button
                  color="error"
                  onClick={() => handleRemoveVoteFlag(idx)}
                  startIcon={<DeleteIcon />}
                >
                  Remove
                </Button>
              </Stack>
            ))}
            <Button variant="outlined" onClick={handleAddVoteFlag}>
              Add Vote Flag
            </Button>
          </Stack>

          {/* Emoji Picker Dialog */}
          {emojiPickerOpen && (
            <div
              style={{
                position: "fixed",
                top: 0,
                left: 0,
                width: "100vw",
                height: "100vh",
                background: "rgba(0,0,0,0.2)",
                zIndex: 1300,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
              onClick={handleCloseEmojiPicker}
            >
              <div onClick={e => e.stopPropagation()}>
                <Suspense fallback={<div>Loading emoji picker...</div>}>
                  <EmojiPicker
                    set="twitter"
                    theme="light"
                    data={emojiData}
                    onEmojiSelect={handleEmojiSelected}
                  />
                </Suspense>
              </div>
            </div>
          )}
        </Stack>
      </Stack>
    </Stack>
  );
}

export default VotemapSettingsPage;
