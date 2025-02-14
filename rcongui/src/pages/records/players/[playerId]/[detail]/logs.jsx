import { useState, useEffect, useMemo } from "react";
import {
  Autocomplete,
  Box,
  Button,
  Divider,
  Stack,
  TextField,
  Grid2 as Grid,
} from "@mui/material";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import { DesktopDateTimePicker } from "@mui/x-date-pickers/DesktopDateTimePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { useOutletContext, useSearchParams, useLoaderData, useSubmit, Form } from "react-router-dom";
import { useGlobalStore } from "@/hooks/useGlobalState";
import dayjs from "dayjs";
import { TableToolbar } from "@/components/table/TableToolbar";
import { TablePagination } from "@/components/table/TablePagination";
import { DebouncedSearchInput } from "@/components/shared/DebouncedSearchInput";
import LiveLogsTable from "@/components/live-logs/LiveLogsTable";
import {
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { logsColumns } from "@/pages/records/game-logs/columns";
import { logActions } from "@/utils/lib";
import downloadLogs from "@/pages/records/game-logs/download";
import DownloadIcon from "@mui/icons-material/Download";
import { DetailCard } from "../styled";
import { cmd } from "@/utils/fetchUtils";

const actionOptions = Object.keys(logActions).map((option) => ({
  label: logActions[option],
  name: option,
}));

export const loader = async ({ request, params }) => {
  const url = new URL(request.url);
  const fields = {
    player_id: params.playerId,
    action: url.searchParams.get("action") ?? "",
    from: url.searchParams.get("from") ? dayjs(url.searchParams.get("from")) : null,
    till: url.searchParams.get("till") ? dayjs(url.searchParams.get("till")) : null,
    limit: url.searchParams.get("limit") ? Number(url.searchParams.get("limit")) : 250,
    time_sort: url.searchParams.get("time_sort") ?? "desc",
    exact_action: url.searchParams.get("exact_action") === "true",
    server_filter: url.searchParams.get("server_filter") ?? "",
  };

  const response = await cmd.GET_HISTORICAL_LOGS({ payload: fields });
  return { logs: response.result };
};

export default function PlayerLogs() {
  const { logs: initialLogs } = useLoaderData();
  const { profile } = useOutletContext();
  const [searchParams, setSearchParams] = useSearchParams();
  const submit = useSubmit();
  const server = useGlobalStore((state) => state.serverState);
  const otherServers = useGlobalStore((state) => state.servers);
  const [logs, setLogs] = useState(initialLogs);

  useEffect(() => {
    setLogs(initialLogs);
  }, [initialLogs]);

  const [formFields, setFormFields] = useState({
    action: searchParams.get("action") || "",
    limit: searchParams.get("limit") || 250,
    time_sort: searchParams.get("time_sort") || "desc",
    exact_action: searchParams.get("exact_action") === "true",
    server_filter: searchParams.get("server_filter") || "",
    from: searchParams.get("from") ? dayjs(searchParams.get("from")) : null,
    till: searchParams.get("till") ? dayjs(searchParams.get("till")) : null,
  });

  const table = useReactTable({
    data: logs ?? [],
    columns: logsColumns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    initialState: {
      pagination: {
        pageIndex: 0,
        pageSize: 100,
      },
    },
  });

  const handleInputChange = (e) => {
    const { name, value, checked, type } = e.target;
    let newValue = value;

    if (type === "checkbox") {
      newValue = checked;
    }

    setFormFields((prev) => ({
      ...prev,
      [name]: newValue,
    }));
  };

  const handleDateChange = (name, value) => {
    setFormFields((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleActionChange = (event, newValue) => {
    setFormFields((prev) => ({
      ...prev,
      action: newValue?.name || "",
    }));
  };

  const handleClear = () => {
    setFormFields({
      action: "",
      limit: 250,
      time_sort: "desc",
      exact_action: false,
      server_filter: "",
      from: null,
      till: null,
    });
  };

  const handleDownload = () => {
    downloadLogs(logs);
  };

  const serverOptions = useMemo(() => {
    if (!server || !otherServers) return [];

    const options = [server, ...otherServers].map((server) => ({
      label: server.name,
      value: server.server_number,
    }));

    return options;
  }, [server, otherServers]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    
    Object.entries(formFields).forEach(([key, value]) => {
      if (value !== "" && value !== null) {
        if (key === 'from' || key === 'till') {
          formData.append(key, value.toISOString());
        } else {
          formData.append(key, value);
        }
      }
    });

    if (formData.get("server_filter") === "0") {
      formData.set("server_filter", "");
    }

    submit(formData, {
      method: "GET",
      replace: true,
    });
  };

  return (
    <Stack spacing={1}>
      <Stack spacing={1} sx={{ mt: 2 }}>
        <Form onSubmit={handleSubmit}>
          <Grid container spacing={2} sx={{ p: 2 }}>
            {/* Action and Exact Switch */}
            <Grid item size={{ xs: 12, sm: 6 }}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <Autocomplete
                  aria-labelledby="action_label"
                  fullWidth
                  freeSolo
                  options={actionOptions}
                  getOptionLabel={(option) => option.name}
                  renderOption={(props, option) => {
                    const { key, ...optionProps } = props;
                    return (
                      <Box key={option.name} component="li" {...optionProps}>
                        {logActions[option.name]} {option.name}
                      </Box>
                    );
                  }}
                  value={
                    actionOptions.find((o) => o.name === formFields.action) || null
                  }
                  onChange={handleActionChange}
                  renderInput={(params) => (
                    <TextField name="action" {...params} label="Action" />
                  )}
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={formFields.exact_action}
                      name="exact_action"
                      onChange={handleInputChange}
                      color="primary"
                    />
                  }
                  label="Exact"
                  labelPlacement="end"
                />
              </Stack>
            </Grid>

            {/* Server Filter */}
            <Grid item size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth>
                <InputLabel id="server_filter_label">Server filter</InputLabel>
                <Select
                  labelId="server_filter_label"
                  name="server_filter"
                  value={formFields.server_filter}
                  onChange={handleInputChange}
                  label="Server filter"
                >
                  <MenuItem value={0}>All servers</MenuItem>
                  {serverOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Limit */}
            <Grid item size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Limit"
                name="limit"
                type="number"
                value={formFields.limit}
                onChange={handleInputChange}
              />
            </Grid>

            {/* Time Sort */}
            <Grid item size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth>
                <InputLabel id="time_sort_label">Time sort</InputLabel>
                <Select
                  labelId="time_sort_label"
                  name="time_sort"
                  value={formFields.time_sort}
                  onChange={handleInputChange}
                >
                  <MenuItem value={"desc"}>From newest</MenuItem>
                  <MenuItem value={"asc"}>From oldest</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Date Time Pickers */}
            <Grid item size={{ xs: 12, sm: 6 }}>
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DesktopDateTimePicker
                  value={formFields.from}
                  label="From time"
                  name="from"
                  onChange={(value) => handleDateChange('from', value)}
                  format="YYYY/MM/DD HH:mm"
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item size={{ xs: 12, sm: 6 }}>
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DesktopDateTimePicker
                  label="Till time"
                  name="till"
                  onChange={(value) => handleDateChange('till', value)}
                  format="YYYY/MM/DD HH:mm"
                  value={formFields.till}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </LocalizationProvider>
            </Grid>

            {/* Buttons */}
            <Grid item size={{ xs: 12, sm: 6 }}>
              <Button
                fullWidth
                onClick={handleClear}
                variant="outlined"
                color="error"
                size="large"
              >
                Clear
              </Button>
            </Grid>

            <Grid item size={{ xs: 12, sm: 6 }}>
              <Button
                fullWidth
                variant="contained"
                color="primary"
                size="large"
                type="submit"
              >
                Search
              </Button>
            </Grid>
          </Grid>
        </Form>

        <DetailCard elevation={0} variant="outlined" sx={{ flexGrow: 1 }}>
          <TableToolbar>
            <DebouncedSearchInput
              placeholder={"Search logs"}
              onChange={(value) => {
                table.getColumn("content")?.setFilterValue(value);
              }}
              sx={{ maxWidth: (theme) => theme.breakpoints.values.sm }}
            />
            <Box sx={{ flexGrow: 1 }} />
            <TablePagination table={table} />
            <Divider flexItem orientation="vertical" />
            <Button
              size="small"
              variant="contained"
              color="primary"
              onClick={handleDownload}
              startIcon={<DownloadIcon />}
            >
              Download
            </Button>
          </TableToolbar>
          <LiveLogsTable
            table={table}
            config={{
              actions: [],
              fontSize: "small",
              density: "dense",
            }}
          />
          <TableToolbar>
            <Box sx={{ flexGrow: 1 }} />
            <TablePagination table={table} />
          </TableToolbar>
        </DetailCard>
      </Stack>
    </Stack>
  );
} 