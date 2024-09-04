import React, { useEffect } from "react";
import {
  postData,
  showResponse,
} from "../../utils/fetchUtils";
import Grid from "@mui/material/Unstable_Grid2";
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
import MUIDataTable from "mui-datatables";
import moment from "moment";
import Link from "@mui/material/Link";

const LogsFilter = ({ onSubmit, onChange }) => {
  const [name, setName] = React.useState("");
  const [playerId, setPlayerId] = React.useState("");
  const [type, setType] = React.useState("");
  const [server, setServer] = React.useState("");
  const [from, setFrom] = React.useState(null);
  const [till, setTill] = React.useState(null);
  const [limit, setLimit] = React.useState(1000);
  const [exactPlayer, setExactPlayer] = React.useState(false);
  const [exactAction, setExactAction] = React.useState(false);
  const [order, setOrder] = React.useState("desc");

  return (
    (<Grid container spacing={1}>
      <Grid xs={12} >
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
              {/* <MuiPickersUtilsProvider utils={MomentUtils}>
                <DateTimePicker
                  label="From time"
                  format="YYYY/MM/DD HH:mm"
                  value={from}
                  onChange={setFrom}
                />
              </MuiPickersUtilsProvider> */}
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DesktopDateTimePicker
                  label="From time"
                  onChange={(value) => console.log(value)} // send value to hook form
                  format='LLL'
                />
              </LocalizationProvider>
            </Grid>
            <Grid>
              {/* <MuiPickersUtilsProvider utils={MomentUtils}>
                <DateTimePicker
                  label="Till time"
                  format="YYYY/MM/DD HH:mm"
                  value={till}
                  onChange={setTill}
                />
              </MuiPickersUtilsProvider> */}
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DesktopDateTimePicker
                label="Till time"
                onChange={(value) => console.log(value)} // send value to hook form
                format='LLL'
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

class LogsHistory extends React.Component {
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

  columns = [
    {
      name: "event_time",
      label: "Time",
      options: {
        customBodyRenderLite: (dataIndex) =>
          moment(this.state.logs[dataIndex]?.event_time)
            .local()
            .format("ddd Do MMM HH:mm:ss"),
      },
    },
    { name: "type", label: "Type" },
    { name: "content", label: "Content" },
    {
      name: "player1_id",
      label: "Name 1",
      options: {
        customBodyRenderLite: (dataIndex) => {
          let id = this.state.logs[dataIndex]?.player1_id;
          let name = this.state.logs[dataIndex]?.player1_name;
          return id ? (
            <Link
              color="inherit"
              target="_blank"
              href={`/api/get_player_profile?player_id=${id}`}
            >
              {name}
            </Link>
          ) : (
            name
          );
        },
      },
    },
    {
      name: "player2_id",
      label: "Name 2",
      options: {
        customBodyRenderLite: (dataIndex) => {
          let id = this.state.logs[dataIndex]?.player2_id;
          let name = this.state.logs[dataIndex]?.player2_name;
          return id ? (
            <Link
              color="inherit"
              target="_blank"
              href={`/api/get_player_profile?player_id=${id}`}
            >
              {name}
            </Link>
          ) : (
            name
          );
        },
      },
    },
    { name: "server", label: "Server" },
  ];

  options = {
    filter: false,
    rowsPerPage: 10,
    selectableRows: "none",
    rowsPerPageOptions: [10, 25, 50, 100, 250, 500, 1000],
    onChangeRowsPerPage: this.saveRowsPerPage,
    onDownload: () => {
      this.handleDownload();
      return false;
    },
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
        <Grid xs={12}>
          <LogsFilter onSubmit={this.getHistoricalLogs} />
        </Grid>
        {isLoading ? (
          <Grid xs={12} >
            <LinearProgress color="secondary" />
          </Grid>
        ) : (
          ""
        )}
        <Grid xs={12}>
          <Grid container justifyContent="center">
            <Grid>
              <Grid container justifyContent="center">
                <Grid>
                  <MUIDataTable
                    title={"Game logs"}
                    data={this.state.logs}
                    columns={this.columns}
                    options={this.options}
                  />
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Grid>)
    );
  }
}

export default LogsHistory;
