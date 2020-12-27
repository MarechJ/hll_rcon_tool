import React from "react";
import { toast } from "react-toastify";
import {
  postData,
  showResponse,
  get,
  handle_http_errors,
} from "../../utils/fetchUtils";
import Grid from "@material-ui/core/Grid";
import { makeStyles } from "@material-ui/core/styles";
import _ from "lodash";
import LogsTable from "./logTable";
import MomentUtils from "@date-io/moment";
import { DateTimePicker, MuiPickersUtilsProvider } from "@material-ui/pickers";
import { Button, TextField } from "@material-ui/core";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Switch from "@material-ui/core/Switch";

const useStyles = makeStyles((theme) => ({
  flexContainer: {
    display: "flex",
    flexDirection: "row",
  },
  margin: {
    margin: theme.spacing(2),
  },
}));

const LogsFilter = ({ onSubmit }) => {
  const classes = useStyles();
  const [name, setName] = React.useState("");
  const [steamId64, setSteamId64] = React.useState("");
  const [type, setType] = React.useState("");
  const [server, setServer] = React.useState("");
  const [from, setFrom] = React.useState(null);
  const [till, setTill] = React.useState(null);
  const [limit, setLimit] = React.useState(1000);
  const [exactPlayer, setExactPlayer] = React.useState(false);
  const [exactAction, setExactAction] = React.useState(false);
  const [order, setOrder] = React.useState("desc");

  return (
    <Grid container spacing={1}>
      <Grid item xs={12} className={classes.margin}>
        <form className={classes.flexContainer}>
          <Grid container spacing={1} justify="space-evenly">
            <Grid item>
              <TextField
                label="Steam id"
                value={steamId64}
                onChange={(e) => setSteamId64(e.target.value)}
              />
            </Grid>
            <Grid item>
              <TextField
                label="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <FormControlLabel
                value={exactPlayer}
                onChange={(event) => setExactPlayer(event.target.checked)}
                control={<Switch color="primary" />}
                label="Exact"
                color="Secondary"
                labelPlacement="top"
                className="MuiFormLabel-root"
              />
            </Grid>
            <Grid item>
              <TextField
                label="Type"
                value={type}
                onChange={(e) => setType(e.target.value)}
              />
              <FormControlLabel
                value={exactAction}
                onChange={(event) => setExactAction(event.target.checked)}
                control={<Switch color="primary" />}
                label="Exact"
                color="Secondary"
                labelPlacement="top"
                className="MuiFormLabel-root"
              />
            </Grid>
            <Grid item>
              <TextField
                label="Server filter"
                value={server}
                onChange={(e) => setServer(e.target.value)}
              />
            </Grid>
            <Grid item>
              <TextField
                label="Limit"
                type="number"
                value={limit}
                onChange={(e) => setLimit(e.target.value)}
              />
            </Grid>
            <Grid item>
              <MuiPickersUtilsProvider utils={MomentUtils}>
                <DateTimePicker
                  label="From time"
                  format="YYYY/MM/DD HH:mm"
                  value={from}
                  onChange={setFrom}
                />
              </MuiPickersUtilsProvider>
            </Grid>
            <Grid item>
              <MuiPickersUtilsProvider utils={MomentUtils}>
                <DateTimePicker
                  label="Last seen until"
                  format="YYYY/MM/DD HH:mm"
                  value={till}
                  onChange={setTill}
                />
              </MuiPickersUtilsProvider>
            </Grid>
            <Grid item>
              <FormControl className={classes.formControl}>
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
            <Grid item>
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
                    steamId64,
                    from,
                    till,
                    limit,
                    order,
                    exactPlayer,
                    exactAction
                  );
                }}
                onClick={(e) => {
                  e.preventDefault();
                  onSubmit(
                    name,
                    type,
                    steamId64,
                    from,
                    till,
                    limit,
                    order,
                    exactPlayer,
                    exactAction
                  );
                }}
              >
                load
              </Button>
            </Grid>
          </Grid>
        </form>
      </Grid>
    </Grid>
  );
};

class LogsHistory extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      logs: [],
    };

    this.getHistoricalLogs = this.getHistoricalLogs.bind(this);
  }

  getHistoricalLogs(
    name = null,
    type = null,
    steamId64 = null,
    from = null,
    till = null,
    limit = 1000,
    timeSort = "desc",
    exactPlayer = false,
    exactAction = false
  ) {
    postData(`${process.env.REACT_APP_API_URL}get_historical_logs`, {
      player_name: name,
      log_type: type,
      steam_id_64: steamId64,
      from: from,
      till: till,
      limit: limit,
      time_sort: timeSort,
      exact_player: exactPlayer,
      exact_action: exactAction,
    })
      .then((res) => showResponse(res, "get_historical_logs", false))
      .then((res) => {
        console.log(res);
        this.setState({ logs: res.result ? res.result : [] });
      });
  }

  componentDidMount() {
    this.getHistoricalLogs();
  }

  render() {
    console.log(this.state.logs);

    return (
      <Grid container>
        <Grid item xs={12}>
          <LogsFilter onSubmit={this.getHistoricalLogs} />
        </Grid>
        <Grid item xs={12}>
          <LogsTable logs={this.state.logs} />
        </Grid>
      </Grid>
    );
  }
}

export default LogsHistory;
