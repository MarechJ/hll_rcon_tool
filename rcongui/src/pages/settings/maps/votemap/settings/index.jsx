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
  Box,
  Button,
  CircularProgress,
  Divider,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
  useTheme,
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
import Emoji from "@/components/shared/Emoji";
import AddCircleIcon from "@mui/icons-material/AddCircle";

function VotemapSettingsPage() {
  const loaderData = useLoaderData();
  const queryClient = useQueryClient();
  const theme = useTheme();

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
  const [emojiPickerMode, setEmojiPickerMode] = useState(null);

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

  const handleRemoveVoteFlag = (index) => {
    setWorkingConfig((prev) => ({
      ...prev,
      vote_flags: prev.vote_flags.filter((_, i) => i !== index),
    }));
  };

  const handleRemovePlayerChoiceFlag = (index) => {
    setWorkingConfig((prev) => ({
      ...prev,
      player_choice_flags: prev.player_choice_flags.filter(
        (_, i) => i !== index
      ),
    }));
  };

  const handleRemoveVoteBanFlag = (index) => {
    setWorkingConfig((prev) => ({
      ...prev,
      vote_ban_flags: prev.vote_ban_flags.filter(
        (_, i) => i !== index
      ),
    }));
  };

  const handleRemoveAllowOnlyFlag = (index) => {
    setWorkingConfig((prev) => ({
      ...prev,
      vote_ban_flags: prev.vote_ban_flags.filter(
        (_, i) => i !== index
      ),
    }));
  };

  const handleRemoveFlag = (index) => {
    switch (emojiPickerMode) {
      case "update_vote_flag":
        handleRemoveVoteFlag(index);
        break;
      case "update_player_choice_flag":
        handleRemovePlayerChoiceFlag(index);
        break
      case "update_vote_ban_flag":
        handleRemoveVoteBanFlag(index);
        break
      case "update_allow_flag_only":
        handleRemoveAllowOnlyFlag(index);
        break
      default:
        break;
    }
  };

  const handlePlayerChoiceFlagChange = (index, value) => {
    setWorkingConfig((prev) => {
      const updated = [...(prev.player_choice_flags || [])];
      updated[index] = value;
      return { ...prev, player_choice_flags: updated };
    });
  };

  const handleAddPlayerChoiceFlag = (index, value) => {
    setWorkingConfig((prev) => {
      const updated = (prev.player_choice_flags || []).concat(value);
      return { ...prev, player_choice_flags: updated };
    });
  };

  const handleVoteBanFlagChange = (index, value) => {
    setWorkingConfig((prev) => {
      const updated = [...(prev.vote_ban_flags || [])];
      updated[index] = value;
      return { ...prev, vote_ban_flags: updated };
    });
  };

  const handleAllowOnlyFlagChange = (index, value) => {
    setWorkingConfig((prev) => {
      const updated = [...(prev.allow_flag_only || [])];
      updated[index] = value;
      return { ...prev, allow_flag_only: updated };
    });
  };

  const handleAddVoteBanFlag = (index, value) => {
    setWorkingConfig((prev) => {
      const updated = (prev.vote_ban_flags || []).concat(value);
      return { ...prev, vote_ban_flags: updated };
    });
  };

  const handleAddVoteFlag = (index, value) => {
    setWorkingConfig((prev) => {
      const another = { flag: value, vote_count: 1 };
      const updated = (prev.vote_flags || []).concat(another);
      return { ...prev, vote_flags: updated };
    });
  };

  const handleAddAllowOnlyFlag = (index, value) => {
    setWorkingConfig((prev) => {
      const another = { flag: value, vote_count: 1 };
      const updated = (prev.allow_flag_only || []).concat(another);
      return { ...prev, allow_flag_only: updated };
    });
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

  const handleOpenEmojiPicker = (index, mode) => {
    setEmojiPickerIndex(index);
    setEmojiPickerOpen(true);
    setEmojiPickerMode(mode);
  };

  const handleCloseEmojiPicker = () => {
    setEmojiPickerIndex(null);
    setEmojiPickerOpen(false);
    setEmojiPickerMode(null);
  };

  const handleEmojiSelected = (emoji) => {
    if (emojiPickerIndex !== null && emojiPickerMode !== null) {
      switch (emojiPickerMode) {
        case "update_vote_flag":
          handleVoteFlagChange(emojiPickerIndex, "flag", emoji.native);
          break;
        case "update_player_choice_flag":
          handlePlayerChoiceFlagChange(emojiPickerIndex, emoji.native);
          break;
        case "update_vote_ban_flag":
            handleVoteBanFlagChange(emojiPickerIndex, emoji.native);
            break;
        case "update_allow_flag_only":
          handleAllowOnlyFlagChange(emojiPickerIndex, emoji.native);
          break;
        case "add_player_choice_flag":
          handleAddPlayerChoiceFlag(emojiPickerIndex, emoji.native);
          break;
        case "add_vote_ban_flag":
          handleAddVoteBanFlag(emojiPickerIndex, emoji.native);
          break;
        case "add_vote_flag":
          handleAddVoteFlag(emojiPickerIndex, emoji.native);
          break;
        case "add_allow_flag_only":
          handleAddAllowOnlyFlag(emojiPickerIndex, emoji.native);
          break;
        default:
          break;
      }
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
          <Typography variant="subtitle1">Vote Count Flags</Typography>
          <Typography variant="caption">
            Players with a listed flag have their vote counted n times (use
            highest value if multiple flags and if VIP;  0 ≤ n ≤ 100).
          </Typography>
          <Stack
            direction="row"
            gap={1}
            flexWrap={"wrap"}
            alignItems={"center"}
          >
            {(workingConfig.vote_flags || []).map((item, idx) => (
              <Stack key={idx} direction="row" gap={0.25} alignItems="center">
                <Button
                  variant="outlined"
                  onClick={() => handleOpenEmojiPicker(idx, "update_vote_flag")}
                  sx={{ minWidth: 48, fontSize: 24 }}
                >
                  <Emoji emoji={item.flag || "❓"} />
                </Button>
                <TextField
                  type="number"
                  label="Vote Count"
                  slotProps={{ input: { min: 1, max: 100 } }}
                  value={item.vote_count}
                  onChange={(e) =>
                    handleVoteFlagChange(idx, "vote_count", e.target.value)
                  }
                  sx={{ width: 80 }}
                />
              </Stack>
            ))}
            <IconButton
              variant="outlined"
              onClick={() =>
                handleOpenEmojiPicker(
                  workingConfig.vote_flags.length,
                  "add_vote_flag"
                )
              }
            >
              <AddCircleIcon />
            </IconButton>
          </Stack>

          <Divider flexItem orientation={"horizontal"} />

          {/* Vote Ban Flags Section */}
          <Typography variant="subtitle1">Vote Whitelist Flags</Typography>
          <Typography variant="caption">
            Only players having one of these flags are allowed to use votemap. When no flags provided, everyone is allowed.
          </Typography>
          <Stack direction="row" flexWrap={"wrap"} gap={1} alignItems="center">
            {(workingConfig.allow_flag_only || []).map((item, idx) => (
              <Button
                key={idx}
                variant="outlined"
                onClick={() =>
                  handleOpenEmojiPicker(idx, "update_allow_flag_only")
                }
                sx={{ minWidth: 48, fontSize: 24 }}
              >
                <Emoji emoji={item ?? "❓"} />
              </Button>
            ))}
            <IconButton
              variant="outlined"
              onClick={() =>
                handleOpenEmojiPicker(
                  workingConfig.allow_flag_only.length,
                  "add_allow_flag_only"
                )
              }
            >
              <AddCircleIcon />
            </IconButton>
          </Stack>

          {/* Vote Ban Flags Section */}
          <Typography variant="subtitle1">Vote Ban Flags</Typography>
          <Typography variant="caption">
            Players having one of these flags are banned from voting maps.
          </Typography>
          <Stack direction="row" flexWrap={"wrap"} gap={1} alignItems="center">
            {(workingConfig.vote_ban_flags || []).map((item, idx) => (
              <Button
                key={idx}
                variant="outlined"
                onClick={() =>
                  handleOpenEmojiPicker(idx, "update_vote_ban_flag")
                }
                sx={{ minWidth: 48, fontSize: 24 }}
              >
                <Emoji emoji={item ?? "❓"} />
              </Button>
            ))}
            <IconButton
              variant="outlined"
              onClick={() =>
                handleOpenEmojiPicker(
                  workingConfig.vote_ban_flags.length,
                  "add_vote_ban_flag"
                )
              }
            >
              <AddCircleIcon />
            </IconButton>
          </Stack>

          <Divider flexItem orientation={"horizontal"} />

          {/* Player Choice Flags Section */}
          <Typography variant="subtitle1">Player Choice Whitelist Flags</Typography>
          <Typography variant="caption">
            Players having one of these flags are allowed to run `!vm add`
            commands. When no flags provided, everyone is allowed.
          </Typography>
          <Stack direction="row" flexWrap={"wrap"} gap={1} alignItems="center">
            {(workingConfig.player_choice_flags || []).map((item, idx) => (
              <Button
                key={idx}
                variant="outlined"
                onClick={() =>
                  handleOpenEmojiPicker(idx, "update_player_choice_flag")
                }
                sx={{ minWidth: 48, fontSize: 24 }}
              >
                <Emoji emoji={item ?? "❓"} />
              </Button>
            ))}
            <IconButton
              variant="outlined"
              onClick={() =>
                handleOpenEmojiPicker(
                  workingConfig.player_choice_flags.length,
                  "add_player_choice_flag"
                )
              }
            >
              <AddCircleIcon />
            </IconButton>
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
              <div onClick={(e) => e.stopPropagation()}>
                <Suspense fallback={<div>Loading emoji picker...</div>}>
                  <EmojiPicker
                    set="twitter"
                    theme={theme.palette.mode}
                    data={emojiData}
                    onEmojiSelect={handleEmojiSelected}
                  />
                  {!emojiPickerMode.startsWith("add_") && (
                    <Stack
                      sx={{
                        bgcolor: (theme) => theme.palette.background.paper,
                        borderBottomLeftRadius: (theme) =>
                          theme.shape.borderRadius,
                        borderBottomRightRadius: theme.shape.borderRadius,
                      }}
                      direction={"row"}
                    >
                      <Button
                        onClick={() => {
                          handleRemoveFlag(emojiPickerIndex);
                          handleCloseEmojiPicker();
                        }}
                        sx={{ borderTopLeftRadius: 0, borderTopRightRadius: 0 }}
                        variant="contained"
                        color="error"
                        fullWidth
                      >
                        Remove
                      </Button>
                    </Stack>
                  )}
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
