import React from "react";
import { useStorageState } from "@/hooks/useStorageState";
import { useAsyncInterval } from "@/hooks/useInterval"; // Updated hook with AbortController
import { execute } from "@/utils/fetchUtils";
import Grid from "@mui/material/Grid2";
import {
  Box,
  FormControlLabel,
  Stack,
  Switch,
  Autocomplete,
  TextField,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Skeleton,
} from "@mui/material";
import Log, { Line } from "./Log";
import { debounce } from "lodash"; // Import debounce from lodash

const limitOptions = [
  100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000,
];

const interval = 30; // 30 seconds

const getLogs = (filters) => execute("get_recent_logs", filters);

const LiveLogs = () => {
  // Using custom hook that synchronizes the components state
  // and the browser's local storage
  const [logsConfig, setLogsConfig] = useStorageState("crcon-logs-config", {
    players: [],
    actions: [],
    inclusive: true,
    limit: 500,
    highlighted: false,
  });

  const handleFiltersChange = (newParams) => {
    setLogsConfig((prevConfig) => ({
      ...prevConfig,
      ...newParams,
    }));
  };

  const fetchLogs = React.useCallback(
    () =>
      getLogs({
        end: logsConfig.limit,
        filter_action: logsConfig.actions,
        filter_player: logsConfig.players,
        inclusive_filter: logsConfig.inclusive,
      }),
    [
      logsConfig.players,
      logsConfig.actions,
      logsConfig.inclusive,
      logsConfig.limit,
    ]
  );

  const { data, loading, refresh } = useAsyncInterval(fetchLogs, interval * 1000);

  // Debounce the refresh to avoid multiple calls when filters change rapidly
  const debouncedRefresh = React.useCallback(debounce(refresh, 500), [refresh]);

  // Trigger refresh when filters change
  React.useEffect(() => {
    debouncedRefresh(); // Debounced to prevent frequent rapid requests
  }, [
    logsConfig.players,
    logsConfig.actions,
    logsConfig.inclusive,
    logsConfig.limit,
    debouncedRefresh,
  ]);

  const logsResult = React.useMemo(() => {
    let result;

    result = data?.result;

    if (!result) return {};

    const { logs, actions, players } = result;

    return {
      players,
      actions,
      logs,
    };
  }, [data]);

  const { players = [], actions = [], logs = [] } = logsResult;

  return (
    <Stack sx={{ maxHeight: "calc(var(--DataGrid-headersTotalHeight))" }}>
      {/* FILTERS & CONTROLS */}
      <Grid container columnSpacing={1} alignItems={"center"}>
        <Grid size={{ xs: 12, lg: 2 }}>
          <FormControl fullWidth>
            <InputLabel id="lines-limit-label">Lines limit</InputLabel>
            <Select
              labelId="lines-limit-label"
              id="lines-limit-select"
              label="Lines limit"
              value={logsConfig.limit}
              onChange={(event) => handleFiltersChange({ limit: event.target.value })}
              displayEmpty
            >
              {limitOptions.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid size={{ xs: 12, lg: 3 }}>
          <Autocomplete
            id="filter-by-type"
            multiple
            options={actions ?? []}
            value={logsConfig.actions}
            getOptionLabel={(option) => option}
            filterSelectedOptions
            onChange={(event, value) => handleFiltersChange({ actions: value })}
            renderInput={(params) => (
              <TextField
                {...params}
                variant="outlined"
                label="Filter by type"
              />
            )}
          />
        </Grid>
        <Grid size={{ xs: 12, lg: 3 }}>
          <Autocomplete
            id="filter-by-player"
            multiple
            options={players}
            value={logsConfig.players}
            getOptionLabel={(option) => option}
            filterSelectedOptions
            onChange={(event, value) => {
              handleFiltersChange({ players: value });
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                variant="outlined"
                label="Filter by player"
              />
            )}
          />
        </Grid>
        <Grid size={{ xs: 12, lg: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={logsConfig.inclusive}
                onChange={(event) =>
                  handleFiltersChange({ inclusive: event.target.checked })
                }
              />
            }
            label="Inclusive"
            labelPlacement="top"
          />
        </Grid>
        <Grid size={{ xs: 12, lg: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={logsConfig.highlighted}
                onChange={(event) =>
                  handleFiltersChange({ highlighted: event.target.checked })
                }
              />
            }
            label="Highlight"
            labelPlacement="top"
          />
        </Grid>
      </Grid>
      {/* LOGS */}
      {logs?.length ? (
        <Paper
          sx={{ p: 1, my: 1, overflow: "auto" }}
          className={logsConfig.highlighted && "highlighted"}
        >
          <Line
            sx={{
              display: "inline-flex",
              borderBottom: "1px solid inherit",
              width: "100%",
            }}
            tabIndex={0}
          >
            <Box sx={{ flexBasis: "9.5em" }}>Time</Box>
            <Box sx={{ flexBasis: "16.5em" }}>Action</Box>
            <Box sx={{ flexGrow: 1 }}>Content</Box>
          </Line>
          {logs.map((log, index) => (
            <Log log={log} key={log.raw} />
          ))}
        </Paper>
      ) : (
        <Skeleton variant="rectangular" sx={{ height: "100vh" }} />
      )}
    </Stack>
  );
};

export default LiveLogs;
