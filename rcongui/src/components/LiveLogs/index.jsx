import React, { Suspense } from "react";
import { useStorageState } from "@/hooks/useStorageState";
import { useAsyncInterval } from "@/hooks/useInterval"; // Updated hook with AbortController
import { cmd, execute } from "@/utils/fetchUtils";
import TableChartIcon from "@mui/icons-material/TableChart";
import TableRowsIcon from "@mui/icons-material/TableRows";
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
  ToggleButton,
  lighten,
  darken,
  styled,
  Divider,
  Checkbox,
} from "@mui/material";
import ToggleButtonGroup, {
  toggleButtonGroupClasses,
} from "@mui/material/ToggleButtonGroup";
import { debounce } from "lodash";
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import PlaylistAddCircleIcon from '@mui/icons-material/PlaylistAddCircle';
import { useLoaderData } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { GridToolbar } from "@mui/x-data-grid";
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
const DataGrid = React.lazy(() =>
  import("@mui/x-data-grid").then((module) => ({ default: module.DataGrid }))
);
const LogLine = React.lazy(() => import("./LogLine"));
const Log = React.lazy(() => import("./Log"));

const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;

const StyledToggleButtonGroup = styled(ToggleButtonGroup)(({ theme }) => ({
  [`& .${toggleButtonGroupClasses.grouped}`]: {
    margin: theme.spacing(0.5),
    border: 0,
    borderRadius: theme.shape.borderRadius,
    [`&.${toggleButtonGroupClasses.disabled}`]: {
      border: 0,
    },
  },
  [`& .${toggleButtonGroupClasses.middleButton},& .${toggleButtonGroupClasses.lastButton}`]:
    {
      marginLeft: -1,
      borderLeft: "1px solid transparent",
    },
}));

const columns = [
  { field: "action", headerName: "Action", width: 150 },
  { field: "player", headerName: "Player", width: 150 },
  {
    field: "time",
    headerName: "Time",
    width: 150,
    valueFormatter: (value) => dayjs(value).format("h:mm:ss"),
  },
  { field: "content", headerName: "Content", flex: 1 },
];

const limitOptions = [
  100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000,
];

const interval = 15 * 1000; // 15 seconds

const LiveLogs = ({ initialLogsView }) => {
  // Using custom hook that synchronizes the components state
  // and the browser's local storage
  const [logsConfig, setLogsConfig] = useStorageState("logs-config", {
    players: [],
    actions: [],
    inclusive: true,
    limit: 500,
    highlighted: false,
    tableMode: "table",
  });

  // Use React Query to manage background refetching
  const {
    data: logsView,
    error,
    isLoading,
  } = useQuery({
    queryKey: ["logs", "live"],
    queryFn: cmd.GET_RECENT_LOGS({ params: {
      end: logsConfig.limit,
      filter_action: logsConfig.actions,
      filter_player: logsConfig.players,
      inclusive_filter: logsConfig.inclusive,
    }}),
    initialData: initialLogsView,
    refetchInterval: interval, // Polling interval for updates
  });

  const rows = React.useMemo(() => {
    if (!logsView || !logsView.logs) {
      return [];
    }

    return logsView.logs.map((log, index) => ({
      id: index,
      time: log.event_time ?? "N/A", // Handle missing fields gracefully
      action: log.action ?? "N/A",
      player: log.player_name_1 ?? "N/A",
      content: log.sub_content ?? "",
    }));
  }, [logsView]);

  const handleFiltersChange = (newParams) => {
    setLogsConfig((prevConfig) => ({
      ...prevConfig,
      ...newParams,
    }));
  };

  return (
    <Stack>
      {/* FILTERS & CONTROLS */}
      <Paper
        elevation={0}
        sx={(theme) => ({
          display: "flex",
          border: `1px solid ${theme.palette.divider}`,
          flexWrap: "wrap",
          alignItems: 'center',
        })}
      >
        <StyledToggleButtonGroup
          value={logsConfig.logsMode}
          exclusive
          size="small"
          onChange={(e, value) => handleFiltersChange({ logsMode: value })}
          aria-label="text alignment"
        >
          <ToggleButton value="table" aria-label="left aligned">
            <TableChartIcon />
          </ToggleButton>
          <ToggleButton value="paper" aria-label="centered">
            <TableRowsIcon />
          </ToggleButton>
        </StyledToggleButtonGroup>
        <Divider flexItem orientation="vertical" sx={{ mx: 0.5, my: 1 }} />
          <ToggleButton value="table" aria-label="left aligned">
            <AutoFixHighIcon />
          </ToggleButton>
          <ToggleButton value="paper" aria-label="centered">
            <PlaylistAddCircleIcon />
          </ToggleButton>
        <Divider flexItem orientation="vertical" sx={{ mx: 0.5, my: 1 }} />
        <FormControl>
          <InputLabel id="lines-limit-label">Lines limit</InputLabel>
          <Select
            labelId="lines-limit-label"
            id="lines-limit-select"
            label="Lines limit"
            value={logsConfig.limit}
            sx={{ width: 120 }}
            size="small"
            onChange={(event) =>
              handleFiltersChange({ limit: event.target.value })
            }
            displayEmpty
          >
            {limitOptions.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <Divider flexItem orientation="vertical" sx={{ mx: 0.5, my: 1 }} />
        <Autocomplete
          id="filter-by-type"
          limitTags={1}
          multiple
          disableCloseOnSelect
          size="small"
          renderOption={(props, option, { selected }) => {
            const { key, ...optionProps } = props;
            return (
              <li key={key} {...optionProps}>
                <Checkbox
                  icon={icon}
                  checkedIcon={checkedIcon}
                  style={{ marginRight: 8 }}
                  checked={selected}
                />
                {option}
              </li>
            );
          }}
          options={logsView?.actions ?? []}
          value={logsConfig.actions}
          getOptionLabel={(option) => option}
          filterSelectedOptions
          onChange={(event, value) => handleFiltersChange({ actions: value })}
          renderInput={(params) => (
            <TextField {...params} sx={{ width: 250 }} variant="outlined" label="Filter by type" />
          )}
        />
        <Divider flexItem orientation="vertical" sx={{ mx: 0.5, my: 1 }} />
        <Autocomplete
          id="filter-by-player"
          limitTags={1}
          multiple
          disableCloseOnSelect
          size="small"
          options={logsView?.players ?? []}
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
              sx={{ width: 200 }}
            />
          )}
          renderOption={(props, option, { selected }) => {
            const { key, ...optionProps } = props;
            return (
              <li key={key} {...optionProps}>
                <Checkbox
                  icon={icon}
                  checkedIcon={checkedIcon}
                  style={{ marginRight: 8 }}
                  checked={selected}
                />
                {option}
              </li>
            );
          }}
        />
      </Paper>
      <Suspense
        fallback={<Skeleton variant="rectangular" sx={{ height: "100vh" }} />}
      >
        {logsConfig.logsMode === "table" ? (
          <DataGrid
            density="compact"
            rows={rows}
            columns={columns}
            loading={isLoading}
            pageSize={100}
            pagination
            slots={{
              toolbar: GridToolbar,
              // Use custom FilterPanel only for deep modification
              // FilterPanel: MyCustomFilterPanel,
            }}
          />
        ) : (
          <Paper
            sx={{ p: 1, my: 1, overflow: "auto" }}
            className={logsConfig.highlighted && "highlighted"}
          >
            <LogLine
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
            </LogLine>
            {logsView.logs.map((log, index) => (
              <Log log={log} key={log.raw} />
            ))}
          </Paper>
        )}
      </Suspense>

      {error && <div>Error loading logs: {error.message}</div>}
    </Stack>
  );
};

export default LiveLogs;
