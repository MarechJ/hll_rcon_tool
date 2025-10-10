import React, { useEffect, useState } from "react";
import {
  Autocomplete,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  FormControl,
  Grid2 as Grid,
  Input,
  InputLabel,
  MenuItem,
  Select,
  Slider,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import SaveIcon from "@mui/icons-material/Save";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";
import {
  getHelpText,
  getMarks,
  getMaxValue,
  getMinValue,
  getStep,
} from "./utils";
import Padlock from "@/components/shared/Padlock";
import { toast } from "react-toastify";
import { useForm } from "react-hook-form";
import { getMapLayerImageSrc } from "../maps/objectives/helpers";

export const AUTOKICK_KEY = {
  condition: "condition",
  enabled: "enabled",
  minimum_ingame_mods: "minimum_ingame_mods",
  minimum_online_mods: "minimum_online_mods",
};

export const GENERAL_KEY = {
  team_switch_cooldown: "team_switch_cooldown",
  idle_autokick_time: "idle_autokick_time",
  max_ping_autokick: "max_ping_autokick",
  queue_length: "queue_length",
  autobalance_enabled: "autobalance_enabled",
  autobalance_threshold: "autobalance_threshold",
  vip_slots_num: "vip_slots_num",
  votekick_enabled: "votekick_enabled",
  votekick_thresholds: "votekick_thresholds",
};

// Reusable Components
export const SliderInput = ({ keyName, title, value, onChange }) => {
  const committedValue = typeof value === "number" ? value : 0;
  const [tempValue, setTempValue] = useState(committedValue);

  useEffect(() => {
    setTempValue(committedValue);
  }, [committedValue]);

  const commitValue = (next) => {
    const clamped = Math.max(
      getMinValue(keyName),
      Math.min(getMaxValue(keyName), Number(next))
    );
    onChange(clamped);
  };

  return (
    <Box key={keyName} sx={{ width: "100%" }}>
      <Typography variant="h6" id={`${keyName}-slider`} gutterBottom>
        {title}
      </Typography>
      <Grid container spacing={4} sx={{ alignItems: "center" }}>
        <Grid size={{ xs: 10 }}>
          <Slider
            id={`${keyName}-slider`}
            value={tempValue}
            onChange={(event, value) => setTempValue(value)}
            onChangeCommitted={(event, value) => commitValue(value)}
            aria-labelledby={`${keyName}-slider`}
            min={getMinValue(keyName)}
            max={getMaxValue(keyName)}
            marks={getMarks(keyName)}
            step={getStep(keyName)}
            valueLabelDisplay="auto"
            size="small"
            color={tempValue === 0 ? "error" : "primary"}
          />
        </Grid>
        <Grid size={{ xs: 2 }}>
          <Input
            id={`${keyName}-input`}
            value={tempValue}
            size="small"
            onChange={(e) => {
              const raw = e.target.value;
              if (raw === "") {
                setTempValue("");
                return;
              }
              const next = Number(raw);
              if (!Number.isNaN(next)) setTempValue(next);
            }}
            onBlur={() =>
              commitValue(tempValue === "" ? getMinValue(keyName) : tempValue)
            }
            inputProps={{
              step: getStep(keyName),
              min: getMinValue(keyName),
              max: getMaxValue(keyName),
              type: "number",
              "aria-labelledby": `${keyName}-slider`,
            }}
          />
        </Grid>
      </Grid>
      <Typography variant="caption" color="text.secondary">
        {getHelpText(keyName)}
      </Typography>
    </Box>
  );
};

export const ToggleInput = ({ keyName, title, value, onChange }) => {
  return (
    <Box>
      <Typography variant="h6" id={`${keyName}-slider`} gutterBottom>
        {title}
      </Typography>
      <Grid container spacing={4} sx={{ alignItems: "center" }}>
        <Grid size={{ xs: 10 }}>
          <Padlock
            label={value ? "Enabled" : "Disabled"}
            checked={value}
            handleChange={onChange}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export const ThresholdsInput = ({ keyName, title, value: pairs, onChange }) => {
  const addThreshold = () => {
    const startingValue =
      pairs.length > 0 ? Math.max(pairs[pairs.length - 1][0], 1) + 1 : 0;
    const newThreshold = [startingValue, 1];
    onChange([...pairs, newThreshold]);
  };

  const removeThreshold = (index) => {
    const updatedThresholds = pairs.filter((_, i) => i !== index);
    onChange(updatedThresholds);
  };

  const handleThresholdChange = (index, keyIndex) => (event) => {
    const value = event.target.value === "" ? "" : Number(event.target.value);
    const updatedThresholds = [...pairs];
    updatedThresholds[index][keyIndex] = value;
    onChange(updatedThresholds);
  };

  const handleBlurThreshold = (index, keyIndex) => (event) => {
    const [min, max] = [event.target.min, event.target.max];
    const updatedThresholds = [...pairs];
    const threshold = updatedThresholds[index][keyIndex];
    if (threshold < min) {
      updatedThresholds[index][keyIndex] = min;
    } else if (threshold > max) {
      updatedThresholds[index][keyIndex] = max;
    }
    onChange(updatedThresholds);
  };

  return (
    <Stack gap={1}>
      <Typography variant="h6" id={`${keyName}-title`} gutterBottom>
        {title}
      </Typography>
      {pairs.map((threshold, index) => (
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
                disabled={index == 0 || index < pairs.length - 1}
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
                      ? Math.max(pairs[index - 1][0], threshold[1]) + 1
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
                disabled={index == 0 || index < pairs.length - 1}
                value={threshold[1]}
                onChange={handleThresholdChange(index, 1)}
                onBlur={handleBlurThreshold(index, 1)}
                placeholder="Votes"
                type="number"
                inputProps={{
                  min: 1,
                  max: threshold[0] - 1,
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
      {!pairs.length && (
        <Typography component={"p"} variant="caption" color="text.secondary">
          No thresholds set.
        </Typography>
      )}
      {(!pairs.length || pairs[pairs.length - 1][0] < 50) && (
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
        {getHelpText(keyName)}
      </Typography>
    </Stack>
  );
};

// Reusable Setting Components
export const SliderSetting = ({
  settingKey,
  payloadKey,
  title,
  subheader,
  icon: Icon,
  queryKey,
  mutationFn,
  initialData,
}) => {
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: [queryKey],
    queryFn: () => cmd.GET_SERVER_SETTINGS(),
    initialData,
    select: (data) => {
      if (typeof data[GENERAL_KEY.votekick_thresholds] === "string") {
        data[GENERAL_KEY.votekick_thresholds] = JSON.parse(
          data[GENERAL_KEY.votekick_thresholds]
        );
      }
      return data[settingKey];
    },
  });

  const { mutate, isPending } = useMutation({
    mutationFn: (value) =>
      mutationFn({ payload: { [payloadKey]: value }, throwRouteError: false }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKey] });
      toast.success(`${title} updated successfully!`);
    },
    onError: (error) =>
      toast.error(`Failed to update ${title.toLowerCase()}: ${error.message}`),
  });

  const form = useForm({ defaultValues: { [settingKey]: data || 0 } });

  React.useEffect(() => {
    if (data !== undefined) {
      form.reset({ [settingKey]: data });
    }
  }, [data, form]);

  const onSubmit = form.handleSubmit((values) => mutate(values[settingKey]));

  return (
    <Grid size={{ xs: 12, md: 6 }}>
      <Card
        elevation={2}
        component={"fieldset"}
        form={`${settingKey}-form`}
        sx={{ height: "100%" }}
      >
        <CardHeader
          avatar={<Icon color="primary" />}
          title={title}
          subheader={subheader}
          action={
            <Button
              type="submit"
              form={`${settingKey}-form`}
              variant="contained"
              size="small"
              startIcon={<SaveIcon />}
              disabled={form.formState.isSubmitting || isPending}
            >
              {isPending ? "Saving..." : "Save"}
            </Button>
          }
        />
        <Divider flexItem sx={{ mt: 1, mb: 2 }} />
        <CardContent>
          <Box component="form" id={`${settingKey}-form`} onSubmit={onSubmit}>
            <SliderInput
              keyName={settingKey}
              title={""}
              value={form.watch(settingKey)}
              onChange={(value) => form.setValue(settingKey, value)}
            />
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
};

export const ToggleSetting = ({
  settingKey,
  payloadKey,
  title,
  subheader,
  icon: Icon,
  queryKey,
  mutationFn,
  initialData,
}) => {
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: [queryKey],
    queryFn: () => cmd.GET_SERVER_SETTINGS(),
    initialData,
    select: (data) => {
      if (typeof data[GENERAL_KEY.votekick_thresholds] === "string") {
        data[GENERAL_KEY.votekick_thresholds] = JSON.parse(
          data[GENERAL_KEY.votekick_thresholds]
        );
      }
      return data[settingKey];
    },
  });

  const { mutate, isPending } = useMutation({
    mutationFn: (value) =>
      mutationFn({ payload: { [payloadKey]: value }, throwRouteError: false }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKey] });
      toast.success(`${title} updated successfully!`);
    },
    onError: (error) =>
      toast.error(`Failed to update ${title.toLowerCase()}: ${error.message}`),
  });

  const form = useForm({ defaultValues: { [settingKey]: data || false } });

  React.useEffect(() => {
    if (data !== undefined) {
      form.reset({ [settingKey]: data });
    }
  }, [data, form]);

  const onSubmit = form.handleSubmit((values) => mutate(values[settingKey]));

  return (
    <Grid size={{ xs: 12, md: 6 }}>
      <Card
        elevation={2}
        component={"fieldset"}
        form={`${settingKey}-form`}
        sx={{ height: "100%" }}
      >
        <CardHeader
          avatar={<Icon color="primary" />}
          title={title}
          subheader={subheader}
          action={
            <Button
              type="submit"
              form={`${settingKey}-form`}
              variant="contained"
              size="small"
              startIcon={<SaveIcon />}
              disabled={form.formState.isSubmitting || isPending}
            >
              {isPending ? "Saving..." : "Save"}
            </Button>
          }
        />
        <Divider flexItem sx={{ mt: 1, mb: 2 }} />
        <CardContent>
          <Box component="form" id={`${settingKey}-form`} onSubmit={onSubmit}>
            <ToggleInput
              keyName={settingKey}
              title={""}
              value={form.watch(settingKey)}
              onChange={(checked) => form.setValue(settingKey, checked)}
            />
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
};

export const ThresholdsSetting = ({
  settingKey,
  payloadKey,
  title,
  subheader,
  icon: Icon,
  queryKey,
  mutationFn,
  initialData,
}) => {
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: [queryKey],
    queryFn: () => cmd.GET_SERVER_SETTINGS(),
    initialData,
    select: (data) => {
      if (typeof data[GENERAL_KEY.votekick_thresholds] === "string") {
        data[GENERAL_KEY.votekick_thresholds] = JSON.parse(
          data[GENERAL_KEY.votekick_thresholds]
        );
      }
      return data[settingKey];
    },
  });

  const { mutate, isPending } = useMutation({
    mutationFn: (value) =>
      mutationFn({
        payload: { [payloadKey]: value },
        throwRouteError: false,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKey] });
      toast.success(`${title} updated successfully!`);
    },
    onError: (error) =>
      toast.error(`Failed to update ${title.toLowerCase()}: ${error.message}`),
  });

  const form = useForm({ defaultValues: { [settingKey]: data || [] } });

  React.useEffect(() => {
    if (data !== undefined) {
      form.reset({ [settingKey]: data });
    }
  }, [data, form]);

  const onSubmit = form.handleSubmit((values) => mutate(values[settingKey]));

  return (
    <Grid size={{ xs: 12, md: 6 }}>
      <Card
        elevation={2}
        component={"fieldset"}
        form={`${settingKey}-form`}
        sx={{ height: "100%" }}
      >
        <CardHeader
          avatar={<Icon color="primary" />}
          title={title}
          subheader={subheader}
          action={
            <Button
              type="submit"
              form={`${settingKey}-form`}
              variant="contained"
              size="small"
              startIcon={<SaveIcon />}
              disabled={form.formState.isSubmitting || isPending}
            >
              {isPending ? "Saving..." : "Save"}
            </Button>
          }
        />
        <Divider flexItem sx={{ mt: 1, mb: 2 }} />
        <CardContent>
          <Box component="form" id={`${settingKey}-form`} onSubmit={onSubmit}>
            <ThresholdsInput
              keyName={settingKey}
              title={""}
              value={form.watch(settingKey)}
              onChange={(value) => form.setValue(settingKey, value)}
            />
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
};

export const AutoVotekickSetting = ({
  title,
  subheader,
  icon: Icon,
  queryKey,
  mutationFn,
  initialData,
}) => {
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: [queryKey],
    queryFn: () => cmd.GET_VOTEKICK_AUTOTOGGLE_CONFIG(),
    initialData,
  });

  const { mutate, isPending } = useMutation({
    mutationFn: (values) =>
      mutationFn({ payload: values, throwRouteError: false }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKey] });
      toast.success(`${title} updated successfully!`);
    },
    onError: (error) =>
      toast.error(`Failed to update ${title.toLowerCase()}: ${error.message}`),
  });

  const form = useForm({
    defaultValues: {
      [AUTOKICK_KEY.enabled]: data?.[AUTOKICK_KEY.enabled] || false,
      [AUTOKICK_KEY.minimum_ingame_mods]:
        data?.[AUTOKICK_KEY.minimum_ingame_mods] || "",
      [AUTOKICK_KEY.minimum_online_mods]:
        data?.[AUTOKICK_KEY.minimum_online_mods] || "",
      [AUTOKICK_KEY.condition]: data?.[AUTOKICK_KEY.condition] || "AND",
    },
  });

  React.useEffect(() => {
    if (data) {
      form.reset({
        [AUTOKICK_KEY.enabled]: data[AUTOKICK_KEY.enabled],
        [AUTOKICK_KEY.minimum_ingame_mods]:
          data[AUTOKICK_KEY.minimum_ingame_mods],
        [AUTOKICK_KEY.minimum_online_mods]:
          data[AUTOKICK_KEY.minimum_online_mods],
        [AUTOKICK_KEY.condition]: data[AUTOKICK_KEY.condition],
      });
    }
  }, [data, form]);

  const onSubmit = form.handleSubmit((values) => mutate(values));

  return (
    <Grid size={{ xs: 12, md: 6 }}>
      <Card
        elevation={2}
        component={"fieldset"}
        form="auto-votekick-form"
        sx={{ height: "100%" }}
      >
        <CardHeader
          avatar={<Icon color="primary" />}
          title={title}
          subheader={subheader}
          action={
            <Button
              type="submit"
              form="auto-votekick-form"
              variant="contained"
              size="small"
              startIcon={<SaveIcon />}
              disabled={form.formState.isSubmitting || isPending}
            >
              {isPending ? "Saving..." : "Save"}
            </Button>
          }
        />
        <Divider flexItem sx={{ mt: 1, mb: 2 }} />
        <CardContent>
          <Box component="form" id="auto-votekick-form" onSubmit={onSubmit}>
            <Stack gap={2}>
              <ToggleInput
                keyName={AUTOKICK_KEY.enabled}
                title={"Auto Votekick Toggle"}
                value={form.watch(AUTOKICK_KEY.enabled)}
                onChange={(checked) =>
                  form.setValue(AUTOKICK_KEY.enabled, checked)
                }
              />
              <Typography variant="h6" id={`autovotekick-title`} gutterBottom>
                {"Auto Votekick Conditions"}
              </Typography>
              <Stack direction={"row"} gap={1}>
                <FormControl
                  required
                  error={form.watch(AUTOKICK_KEY.minimum_ingame_mods) === ""}
                >
                  <InputLabel htmlFor={`in-game-moderators`}>
                    Minimum in-game moderators
                  </InputLabel>
                  <Input
                    {...form.register(AUTOKICK_KEY.minimum_ingame_mods, {
                      onBlur: (e) => {
                        const clamped = Math.max(0, Number(e.target.value));
                        form.setValue(
                          AUTOKICK_KEY.minimum_ingame_mods,
                          clamped
                        );
                      },
                    })}
                    id={`in-game-moderators`}
                    sx={{ minWidth: 175 }}
                    placeholder="Minimum in-game moderators"
                    type="number"
                    inputProps={{ min: 0 }}
                  />
                </FormControl>
                <FormControl variant="standard">
                  <InputLabel id="and-or-label">AND/OR</InputLabel>
                  <Select
                    {...form.register(AUTOKICK_KEY.condition)}
                    labelId="and-or-label"
                    sx={{ minWidth: 75 }}
                  >
                    <MenuItem value={"AND"}>AND</MenuItem>
                    <MenuItem value={"OR"}>OR</MenuItem>
                  </Select>
                </FormControl>
                <FormControl
                  required
                  error={form.watch(AUTOKICK_KEY.minimum_online_mods) === ""}
                >
                  <InputLabel htmlFor={`online-crcon-moderators`}>
                    Online CRCON moderators
                  </InputLabel>
                  <Input
                    {...form.register(AUTOKICK_KEY.minimum_online_mods, {
                      onBlur: (e) => {
                        const clamped = Math.max(0, Number(e.target.value));
                        form.setValue(
                          AUTOKICK_KEY.minimum_online_mods,
                          clamped
                        );
                      },
                    })}
                    id={`online-crcon-moderators`}
                    sx={{ minWidth: 175 }}
                    placeholder="Minimum online CRCON moderators"
                    type="number"
                    inputProps={{ min: 0 }}
                  />
                </FormControl>
              </Stack>
            </Stack>
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
};

// Reusable Timer Setting Components
export const SliderTimer = ({
  settingKey,
  gameMode,
  title,
  subheader,
  icon: Icon,
  mutationFn,
  initialData,
}) => {
  const { mutate, isPending } = useMutation({
    mutationFn: (value) =>
      mutationFn({
        payload: { game_mode: gameMode, length: value },
        throwRouteError: false,
      }),
    onSuccess: () => {
      toast.success(`${title} updated successfully!`);
    },
    onError: (error) =>
      toast.error(`Failed to update ${title.toLowerCase()}: ${error.message}`),
  });

  const form = useForm({ defaultValues: { [settingKey]: initialData || 0 } });

  const onSubmit = form.handleSubmit((values) => mutate(values[settingKey]));

  return (
    <Grid size={{ xs: 12, md: 6 }}>
      <Card
        elevation={2}
        component={"fieldset"}
        form={`${settingKey}-form`}
        sx={{ height: "100%" }}
      >
        <CardHeader
          avatar={<Icon color="primary" />}
          title={title}
          subheader={subheader}
          action={
            <Button
              type="submit"
              form={`${settingKey}-form`}
              variant="contained"
              size="small"
              startIcon={<SaveIcon />}
              disabled={form.formState.isSubmitting || isPending}
            >
              {isPending ? "Saving..." : "Save"}
            </Button>
          }
        />
        <Divider flexItem sx={{ mt: 1, mb: 2 }} />
        <CardContent>
          <Box component="form" id={`${settingKey}-form`} onSubmit={onSubmit}>
            <SliderInput
              keyName={settingKey}
              title={""}
              value={form.watch(settingKey)}
              onChange={(value) => form.setValue(settingKey, value)}
            />
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
};

/*
Option example 
{
    "id": "foy_warfare",
    "map": {
        "id": "foy",
        "name": "FOY",
        "tag": "FOY",
        "pretty_name": "Foy",
        "shortname": "Foy",
        "allies": {
            "name": "us",
            "team": "allies"
        },
        "axis": {
            "name": "ger",
            "team": "axis"
        },
        "orientation": "vertical"
    },
    "game_mode": "warfare",
    "attackers": null,
    "environment": "day",
    "pretty_name": "Foy Warfare",
    "image_name": "foy-day.webp"
}
*/
export const DynamicWeatherSettings = ({
  options,
  settingKey,
  title,
  subheader,
  icon: Icon,
  mutationFn,
}) => {
  const [selectedMap, setSelectedMap] = useState(options[0].id);
  const [enabled, setEnabled] = useState(false);

  const { mutate, isPending } = useMutation({
    mutationFn: (values) =>
      mutationFn({ payload: values, throwRouteError: false }),
    onSuccess: () => {
      toast.success(`${title} updated successfully!`);
    },
    onError: (error) =>
      toast.error(`Failed to update ${title.toLowerCase()}: ${error.message}`),
  });

  const form = useForm({
    defaultValues: {
      [settingKey]: selectedMap,
      enabled,
    },
  });

  const onSubmit = form.handleSubmit((values) => {
    mutate(values);
  });

  return (
    <Grid size={{ xs: 12, md: 6 }}>
      <Card
        elevation={2}
        component={"fieldset"}
        form={`${settingKey}-form`}
        sx={{ height: "100%" }}
      >
        <CardHeader
          avatar={<Icon color="primary" />}
          title={title}
          subheader={subheader}
          action={
            <Button
              type="submit"
              form={`${settingKey}-form`}
              variant="contained"
              size="small"
              startIcon={<SaveIcon />}
              disabled={form.formState.isSubmitting || isPending}
            >
              {isPending ? "Saving..." : "Save"}
            </Button>
          }
        />
        <Divider flexItem sx={{ mt: 1, mb: 2 }} />
        <CardContent>
          <Stack
            direction={"row"}
            gap={2}
            component="form"
            id={`${settingKey}-form`}
            onSubmit={onSubmit}
          >
            <Autocomplete
              fullWidth
              options={options}
              getOptionLabel={(option) =>
                option?.pretty_name ?? option?.name ?? ""
              }
              value={options.find((map) => map.id === selectedMap) || null}
              onChange={(event, newValue) => {
                const newMapId = newValue?.id || "";
                setSelectedMap(newMapId);
                form.setValue(settingKey, newMapId);
              }}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              renderInput={(params) => (
                <TextField {...params} label="Map Name" fullWidth />
              )}
              renderOption={(props, option) => (
                <Box
                  component="li"
                  sx={{ "& > img": { mr: 2, flexShrink: 0 } }}
                  {...props}
                >
                  <img
                    loading="lazy"
                    width="40"
                    height="24"
                    src={getMapLayerImageSrc(option)}
                    alt={option?.pretty_name || option?.name}
                    style={{ objectFit: "cover", borderRadius: "2px" }}
                  />
                  {option?.pretty_name || option?.name}
                </Box>
              )}
            />
            <Padlock
              label={enabled ? "Enabled" : "Disabled"}
              checked={enabled}
              handleChange={(checked) => {
                setEnabled(checked);
                form.setValue("enabled", checked);
              }}
            />
          </Stack>
        </CardContent>
      </Card>
    </Grid>
  );
};
