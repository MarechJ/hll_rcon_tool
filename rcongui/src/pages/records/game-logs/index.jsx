import { cmd } from "@/utils/fetchUtils";
import Grid from "@mui/material/Grid2";
import { DesktopDateTimePicker } from "@mui/x-date-pickers/DesktopDateTimePicker";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { Button, Stack, TextField } from "@mui/material";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import { useState } from "react";
import { Form, useLoaderData, useNavigation } from "react-router-dom";
import { logsColumns } from "./columns";
import {
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  useReactTable,
} from "@tanstack/react-table";
import LiveLogsTable from "@/components/live-logs/LiveLogsTable";
import { useGlobalStore } from "@/hooks/useGlobalState";
import dayjs from "dayjs";

/*
IT'S POST REQUEST !!!

There is not server side pagination !!!

game log example {
    "content": "[VLK] Dorfieee (76561198178339671)",
    "creation_time": "2025-02-10T18:30:37.535809",
    "event_time": "2025-02-10T18:28:15", 
    "id": 503822,
    "player1_id": "76561198178339671",
    "player1_name": "[VLK] Dorfieee",
    "player2_id": null,
    "player2_name": null,
    "raw": "[46 ms (1739212095)] DISCONNECTED [VLK] Dorfieee (76561198178339671)",
    "server": "1",
    "type": "DISCONNECTED",
    "version": 1,
    "weapon": null
}

live log example {
    "action": "DISCONNECTED",
    "event_time": "2025-02-10T21:02:26",
    "line_without_time": "DISCONNECTED Snuffff (b9b23e7f120d1a00d482fba507a81cc8)",
    "message": "Snuffff (b9b23e7f120d1a00d482fba507a81cc8)",
    "player_id_1": "b9b23e7f120d1a00d482fba507a81cc8",
    "player_id_2": null,
    "player_name_1": "Snuffff", 
    "player_name_2": null,
    "raw": "[1.89 sec (1739221346)] DISCONNECTED Snuffff (b9b23e7f120d1a00d482fba507a81cc8)",
    "relative_time_ms": -2221.716,
    "sub_content": null,
    "timestamp_ms": 1739221346000,
    "version": 1,
    "weapon": null
}

params {
  player_name
  action
  player_id
  from
  till
  limit
  time_sort
  exact_player
  exact_action
  server_filter
}

*/

export const loader = async ({ request }) => {
  const url = new URL(request.url);
  // Get params and set default values if not provided
  const player_name = url.searchParams.get("player_name") ?? "";
  const player_id = url.searchParams.get("player_id") ?? "";
  const action = url.searchParams.get("action") ?? "";
  const from = url.searchParams.get("from") ? dayjs(url.searchParams.get("from")) : null;
  const till = url.searchParams.get("till") ? dayjs(url.searchParams.get("till")) : null;
  const limit = url.searchParams.get("limit") ? Number(url.searchParams.get("limit")) : 500;
  const time_sort = url.searchParams.get("time_sort") ?? "desc";
  const exact_player = url.searchParams.get("exact_player") ?? false;
  const exact_action = url.searchParams.get("exact_action") ?? false;
  const server_filter = url.searchParams.get("server_filter") ?? "";

  const fields = {
    player_name,
    action,
    player_id,
    from,
    till,
    limit,
    time_sort,
    exact_player,
    exact_action,
    server_filter,
  };

  console.log(fields);

  const response = await cmd.GET_HISTORICAL_LOGS({ payload: fields });

  const logs = response.result;

  return {
    logs,
    fields,
  };
};

const GameLogsPage = () => {
  const { logs, fields } = useLoaderData();

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

  return (
    <Stack direction={{ xs: "column", lg: "row" }} spacing={1} sx={{ mt: 2 }}>
      <GameLogsForm fields={fields} />
      <LiveLogsTable
        table={table}
        config={{
          actions: [],
          fontSize: "small",
          density: "dense",
        }}
      />
    </Stack>
  );
};

const GameLogsForm = ({ fields }) => {
  const navigation = useNavigation();
  const server = useGlobalStore((state) => state.serverState);
  const [formFields, setFormFields] = useState({
    player_name: fields.player_name || "",
    player_id: fields.player_id || "",
    action: fields.action || "",
    limit: fields.limit || 100,
    time_sort: fields.time_sort || "desc",
    exact_player: fields.exact_player || false,
    exact_action: fields.exact_action || false,
    server_filter: fields.server_filter || server?.server_number || "",
    from: fields.from ? dayjs(fields.from) : null,
    till: fields.till ? dayjs(fields.till) : null,
  });

  const handleInputChange = (e) => {
    const { name, value, checked } = e.target;
    setFormFields((prev) => ({
      ...prev,
      [name]: e.target.type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    console.log(formFields);
  };

  return (
    <Grid container sx={{ width: '300px' }}>
      <Grid xs={12}>
        <Form>
          <Stack spacing={2} sx={{ p: 2 }}>
            <TextField
              fullWidth
              label="Player ID"
              name="player_id"
              value={formFields.player_id}
              onChange={handleInputChange}
            />
            
            <Stack direction="row" alignItems="center" spacing={1}>
              <TextField
                fullWidth
                label="Name"
                name="player_name"
                value={formFields.player_name}
                onChange={handleInputChange}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={formFields.exact_player}
                    name="exact_player"
                    onChange={handleInputChange}
                    color="primary"
                  />
                }
                label="Exact"
                labelPlacement="end"
              />
            </Stack>

            <Stack direction="row" alignItems="center" spacing={1}>
              <TextField
                fullWidth
                label="Type"
                name="action"
                value={formFields.action}
                onChange={handleInputChange}
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

            <TextField
              fullWidth
              label="Server filter"
              name="server_filter"
              value={formFields.server_filter}
              onChange={handleInputChange}
            />

            <TextField
              fullWidth
              label="Limit"
              name="limit"
              type="number"
              value={formFields.limit}
              onChange={handleInputChange}
            />

            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DesktopDateTimePicker
                value={formFields.from}
                label="From time"
                name="from"
                onChange={handleInputChange}
                format="YYYY/MM/DD HH:mm"
                slotProps={{ textField: { fullWidth: true } }}
              />
            </LocalizationProvider>

            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DesktopDateTimePicker
                label="Till time"
                name="till"
                onChange={handleInputChange}
                format="YYYY/MM/DD HH:mm"
                value={formFields.till}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </LocalizationProvider>

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

            <Button
              fullWidth
              variant="contained"
              color="primary"
              size="large"
              type="submit"
              onClick={handleSubmit}
              disabled={navigation.state === "loading"}
            >
              Search
            </Button>
          </Stack>
        </Form>
      </Grid>
    </Grid>
  );
};

export default GameLogsPage;
