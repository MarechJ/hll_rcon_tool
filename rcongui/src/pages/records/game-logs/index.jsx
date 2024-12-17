import {
  postData,
  showResponse,
} from "@/utils/fetchUtils";
import Grid from "@mui/material/Grid2";
import { DesktopDateTimePicker } from '@mui/x-date-pickers/DesktopDateTimePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { Button, LinearProgress, TextField } from "@mui/material";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import { DataGrid, GridToolbar } from "@mui/x-data-grid";
import dayjs from "dayjs";
import {Component, useState} from "react";

const columns = [
  { field: 'id', headerName: 'ID', width: 70, sortable: false },
  {
    field: 'event_time',
    headerName: 'Time',
    width: 160,
    valueFormatter: (value) => dayjs(value).format('lll')
  },
  {
    field: 'type',
    headerName: 'Type',
    width: 120,
  },
  {
    field: 'content',
    headerName: 'Content',
    flex: 1,
    align: 'left',
    sortable: false,
  },
  { field: 'player1_name', headerName: 'Initiator', width: 120 },
  { field: 'player2_name', headerName: 'Receiver', width: 120 },
  { field: 'server', headerName: 'Server', width: 80 },
];

const LogsFilter = ({ onSubmit, onChange }) => {
  const [name, setName] = useState("");
  const [playerId, setPlayerId] = useState("");
  const [type, setType] = useState("");
  const [server, setServer] = useState("");
  const [from, setFrom] = useState(null);
  const [till, setTill] = useState(null);
  const [limit, setLimit] = useState(1000);
  const [exactPlayer, setExactPlayer] = useState(false);
  const [exactAction, setExactAction] = useState(false);
  const [order, setOrder] = useState("desc");

  return (
    (<Grid container spacing={1}>
      <Grid size={12} >
        <form >
          <Grid container spacing={1} justifyContent="space-evenly">
            <Grid>
              <TextField
                label="Player ID"
                value={playerId}
                onChange={(e) => setPlayerId(e.target.value)}
              />
            </Grid>
            <Grid>
              <TextField
                label="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={exactPlayer}
                    onChange={(event) => setExactPlayer(event.target.checked)}
                    color="primary"
                  />
                }
                label="Exact"
                labelPlacement="top"
                className="MuiFormLabel-root"
              />
            </Grid>
            <Grid>
              <TextField
                label="Type"
                value={type}
                onChange={(e) => setType(e.target.value)}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={exactAction}
                    onChange={(event) => setExactAction(event.target.checked)}
                    color="primary"
                  />
                }
                label="Exact"
                color="Secondary"
                labelPlacement="top"
                className="MuiFormLabel-root"
              />
            </Grid>
            <Grid>
              <TextField
                label="Server filter"
                value={server}
                onChange={(e) => setServer(e.target.value)}
              />
            </Grid>
            <Grid>
              <TextField
                label="Limit"
                type="number"
                value={limit}
                onChange={(e) => setLimit(e.target.value)}
              />
            </Grid>
            <Grid>
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DesktopDateTimePicker
                  value={from}
                  label="From time"
                  onChange={setFrom} // send value to hook form
                  format='YYYY/MM/DD HH:mm'
                />
              </LocalizationProvider>
            </Grid>
            <Grid>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DesktopDateTimePicker
                label="Till time"
                onChange={setTill} // send value to hook form
                format='YYYY/MM/DD HH:mm'
                value={till}
              />
            </LocalizationProvider>
            </Grid>
            <Grid>
              <FormControl >
                <InputLabel id="time_sort_label">Time sort</InputLabel>
                <Select
                  labelId="time_sort_label"
                  value={order}
                  onChange={(e) => setOrder(e.target.value)}
                >
                  <MenuItem value={"desc"}>Descending</MenuItem>
                  <MenuItem value={"asc"}>Ascending</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid>
              <Button
                variant="contained"
                color="primary"
                size="large"
                type="sumbit"
                onSubmit={(e) => {
                  e.preventDefault();
                  onSubmit(
                    name,
                    type,
                    playerId,
                    from,
                    till,
                    limit,
                    order,
                    exactPlayer,
                    exactAction,
                    server
                  );
                }}
                onClick={(e) => {
                  e.preventDefault();
                  onSubmit(
                    name,
                    type,
                    playerId,
                    from,
                    till,
                    limit,
                    order,
                    exactPlayer,
                    exactAction,
                    server
                  );
                }}
              >
                load
              </Button>
            </Grid>
          </Grid>
        </form>
      </Grid>
    </Grid>)
  );
};

class LogsHistory extends Component {
  constructor(props) {
    super(props);

    this.state = {
      logs: [],
      isLoading: false,
      name: null,
      type: null,
      playerId: null,
      from: null,
      till: null,
      limit: 10000,
      timeSort: "desc",
      exactPlayer: false,
      exactAction: false,
      server: null,
      myRowPerPage: window.localStorage.getItem("logs_row_per_page") || 50,
    };

    this.getHistoricalLogs = this.getHistoricalLogs.bind(this);
  }

  saveRowsPerPage = (rowPerPage) => {
    window.localStorage.setItem("logs_row_per_page", rowPerPage);
    this.setState({ myRowPerPage: rowPerPage });
  };

  getHistoricalLogs(
    name = null,
    type = null,
    playerId = null,
    from = null,
    till = null,
    limit = 10000,
    timeSort = "desc",
    exactPlayer = false,
    exactAction = false,
    server = null,
  ) {
    this.setState({
      isLoading: true,
      name: name,
      type: type,
      playerId: playerId,
      from: from,
      till: till,
      limit: limit,
      timeSort: timeSort,
      exactPlayer: exactPlayer,
      exactAction: exactAction,
      server: server,
    });
    postData(`${process.env.REACT_APP_API_URL}get_historical_logs`, {
      player_name: name,
      action: type,
      player_id: playerId,
      from: from,
      till: till,
      limit: limit,
      time_sort: timeSort,
      exact_player: exactPlayer,
      exact_action: exactAction,
      server_filter: server,
    })
      .then((res) => showResponse(res, "get_historical_logs", false))
      .then((res) => {
        this.setState({ logs: res.result ? res.result : [] });
        this.setState({ isLoading: false });
      });
  }

  handleDownload() {
    postData(`${process.env.REACT_APP_API_URL}get_historical_logs_csv`, {
      player_name: this.state.name,
      action: this.state.type,
      player_id: this.state.playerId,
      from: this.state.from,
      till: this.state.till,
      limit: this.state.limit,
      time_sort: this.state.timeSort,
      exact_player: this.state.exactPlayer,
      exact_action: this.state.exactAction,
      server_filter: this.state.server,
    })
      .then((res) => res.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(new Blob([blob]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `log.csv`);
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
      });
  }

  componentDidMount() {
    this.getHistoricalLogs();
  }

  render() {
    const { isLoading } = this.state;

    return (
      (<Grid container>
        <Grid size={12}>
          <LogsFilter onSubmit={this.getHistoricalLogs} />
        </Grid>
        {isLoading ? (
          <Grid size={12} >
            <LinearProgress color="secondary" />
          </Grid>
        ) : (
          ""
        )}
        <Grid size={12}>
        <DataGrid
        rows={this.state.logs}
        columns={columns}
        initialState={{
          pagination: {
            paginationModel: {
              pageSize: 100,
            },
          },
          density: 'compact',
        }}
        pageSizeOptions={[10, 25, 50, 100]}
        slots={{ toolbar: GridToolbar }}
        disableRowSelectionOnClick
      />
        </Grid>
      </Grid>)
    );
  }
}

export default LogsHistory;
