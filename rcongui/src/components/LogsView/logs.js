import React from "react";
import {
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Select from "@material-ui/core/Select";
import Grid from "@material-ui/core/Grid";
import { Button, IconButton, Switch } from "@material-ui/core";
import Autocomplete from "@material-ui/lab/Autocomplete";
import TextField from "@material-ui/core/TextField";
import RefreshIcon from "@material-ui/icons/Refresh";
import Paper from "@material-ui/core/Paper";
import moment from "moment";
import withWidth from "@material-ui/core/withWidth";
import AutoRefreshLine from "../autoRefreshLine";
import ListItemText from "@material-ui/core/ListItemText";
import FullscreenIcon from "@material-ui/icons/Fullscreen";
import FullscreenExitIcon from "@material-ui/icons/FullscreenExit";

const formatClass = (action, classes, highlightLogs) => {
  // if the message is a chat message
  if (highlightLogs) {
    if (action.toLowerCase().includes("chat")) {
      if (action.toLowerCase().includes("allies")) {
        return classes.logsChatAllies;
      }
      if (action.toLowerCase().includes("axis")) {
        return classes.logsChatAxis;
      }
    }
    else if (action.toLowerCase().includes("admin")) {
      return classes.logsAdmin;
    }
    else if (action.toLowerCase().includes("tk")) {
      return classes.logsTK;
    }
    else if (action.toLowerCase().includes("match")) {
      return classes.logsMatch;
    }
    else if (action.toLowerCase().includes("vote")) {
      return classes.logsVote;
    }
    else switch (action.toLowerCase()) {
      case "message":
        return classes.logsMessage;
      case "team kill":
        return classes.logsTeamKill;
      case "kill":
        return classes.logsKill;
      case "teamswitch":
        return classes.logsTeamSwitch;
      case "disconnected":
        return classes.logsDisconnected;
      case "connected":
        return classes.logsConnected;
      default:
        return classes.logs;
    }
  }
  return classes.logs;
};
  
const Selector = ({
  classes,
  defaultValue,
  defaultText,
  values,
  currentValue,
  onChange,
  kind,
  multiple,
}) => (
  <FormControl className={classes.logsControl}>
    <InputLabel shrink>{kind}</InputLabel>
    <Select
      value={currentValue}
      onChange={(e) => onChange(e.target.value)}
      displayEmpty
      multiple={multiple}
    >
      {defaultValue !== undefined ? (
        <MenuItem value={defaultValue}>
          <em>{defaultText}</em>
        </MenuItem>
      ) : (
        ""
      )}
      {values.map((a) => (
        <MenuItem key={a} value={a}>
          {a}
        </MenuItem>
      ))}
    </Select>
  </FormControl>
);

class Logs extends React.Component {
  constructor(props) {
    super(props);
    console.log(
      "logs_action_type",
      JSON.parse(localStorage.getItem("logs_action_type"))
    );
    this.state = {
      logs: [],
      actions: [],
      players: [],
      playersFilter: localStorage.getItem("logs_player_filters")
        ? JSON.parse(localStorage.getItem("logs_player_filters"))
        : [],
      actionsFilter: localStorage.getItem("logs_action_filters")
        ? JSON.parse(localStorage.getItem("logs_action_filters"))
        : [],
      inclusiveFilter:
        localStorage.getItem("logs_action_type") !== null
          ? JSON.parse(localStorage.getItem("logs_action_type"))
          : true,
      limit: localStorage.getItem("logs_limit")
        ? localStorage.getItem("logs_limit")
        : 500,
      limitOptions: [
        100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000,
      ],
      highlightLogs: localStorage.getItem("logs_highlight_logs")
        ? localStorage.getItem("logs_highlight_logs")
        : false,
    };

    this.loadLogs = this.loadLogs.bind(this);
    this.setActionFilter = this.setActionFilter.bind(this);
    this.setActionsFilterInclusivity =
      this.setActionsFilterInclusivity.bind(this);
    this.setLimit = this.setLimit.bind(this);
    this.sethighlightLogs = this.sethighlightLogs.bind(this);
  }

  componentDidMount() {
    setTimeout(() => {
      this.loadLogs();
    }, 1000);
  }

  loadLogs() {
    const { actionsFilter, playersFilter, limit, inclusiveFilter } = this.state;

    return postData(`${process.env.REACT_APP_API_URL}get_recent_logs`, {
      end: limit,
      filter_action: actionsFilter,
      filter_player: playersFilter,
      inclusive_filter: inclusiveFilter,
    })
      .then((response) => showResponse(response, "get_logs"))
      .then((data) => {
        this.setState({
          logs: data.result.logs,
          actions: data.result.actions,
          players: !data.result.players ? [] : data.result.players,
        });
      })
      .catch(handle_http_errors);
  }

  setActionFilter(actionsFilter) {
    this.setState({ actionsFilter }, this.loadLogs);
    localStorage.setItem("logs_action_filters", JSON.stringify(actionsFilter));
  }

  setActionsFilterInclusivity(e) {
    this.setState({ inclusiveFilter: e.target.value }, this.loadLogs);
    localStorage.setItem("logs_action_type", JSON.stringify(e.target.value));
  }

  setLimit(limit) {
    this.setState({ limit }, this.loadLogs);
    localStorage.setItem("logs_limit", limit);
  }

  sethighlightLogs(highlightLogs) {
    this.setState({ highlightLogs });
    localStorage.setItem("logs_highlight_logs", highlightLogs);
  }

  render() {
    const { classes, isFullScreen, onFullScreen } = this.props;
    const {
      logs,
      players,
      actions,
      actionsFilter,
      limit,
      limitOptions,
      inclusiveFilter,
      playersFilter,
      highlightLogs,
    } = this.state;

    return (
      <React.Fragment>
        <Grid container justify="flex-start">
          <Grid
            item
            xs={12}
            className={`${classes.textLeft} ${classes.paddingLeft}`}
          >
            <h1 className={classes.marginBottom}>
              Logs view{" "}
              <IconButton onClick={onFullScreen}>
                {isFullScreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
              </IconButton>
            <FormControlLabel
              control={
                <Switch
                  checked={highlightLogs}
                  onChange={(e) => this.sethighlightLogs(e.target.checked)}
                  color="primary"
                />
              }
              label="Hilite Logs"
              labelPlacement="top"
            />
            </h1>
            <ListItemText secondary="30s auto refresh" />
            <AutoRefreshLine
              className={classes.marginTop}
              intervalFunction={this.loadLogs}
              execEveryMs={30000}
              statusRefreshIntervalMs={500}
              classes={classes}
            />
          </Grid>
        </Grid>
        <Grid container justify="space-around" className={classes.marginBottom}>
          <Grid className={classes.padding} item xs={12} sm={12} md={12} lg={2}>
            <Selector
              classes={classes}
              values={limitOptions}
              onChange={this.setLimit}
              currentValue={limit}
              kind="Show last N lines"
            />
          </Grid>
          <Grid className={classes.padding} item xs={12} sm={12} md={12} lg={2}>
            <FormControl fullWidth>
              <InputLabel shrink>Inclusive/Exclusive</InputLabel>
              <Select
                onChange={this.setActionsFilterInclusivity}
                value={inclusiveFilter}
                defaultValue={true}
              >
                <MenuItem value={true}>Inclusive</MenuItem>
                <MenuItem value={false}>Exclusive</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid className={classes.padding} item xs={12} sm={12} md={12} lg={3}>
            <Autocomplete
              id="tags-outlined"
              multiple
              options={actions}
              value={actionsFilter}
              getOptionLabel={(option) => option}
              filterSelectedOptions
              onChange={(e, value) => this.setActionFilter(value)}
              renderInput={(params) => (
                <TextField
                  className={classes.logsControl}
                  {...params}
                  variant="outlined"
                  label="Filter by type"
                />
              )}
            />
          </Grid>
          <Grid className={classes.padding} item xs={12} sm={12} md={12} lg={4}>
            <Autocomplete
              id="tags-outlined"
              multiple
              options={players.sort()}
              value={playersFilter}
              getOptionLabel={(option) => option}
              filterSelectedOptions
              onChange={(e, value) => {
                this.setState(
                  { playersFilter: value ? value : "" },
                  this.loadLogs
                );
                if (value) {
                  localStorage.setItem(
                    "logs_player_filters",
                    JSON.stringify(value)
                  );
                }
              }}
              renderInput={(params) => (
                <TextField
                  className={classes.logsControl}
                  {...params}
                  variant="outlined"
                  label="Filter by player"
                />
              )}
            />
          </Grid>
          <Grid className={classes.padding} item xs={12} sm={12} md={12} lg={1}>
            <Button
              className={classes.logsControl}
              disableElevation
              size="large"
              variant="outlined"
              onClick={this.loadLogs}
            >
              <RefreshIcon />
            </Button>
          </Grid>
        </Grid>
        <Grid container justify="center" alignItems="center">
          <Grid item className={classes.padding} xs={12}>
            <Paper className={classes.paperLogs}>
              {logs.map((l) => (
                <pre key={l.raw} className={formatClass(l.action, classes, highlightLogs)}>
                  {moment(new Date(l.timestamp_ms)).format(
                    "HH:mm:ss - ddd, MMM D"
                  ) +
                    "\t" +
                    l.action.padEnd(20) +
                    l.message}
                </pre>
              ))}
            </Paper>
          </Grid>
        </Grid>
      </React.Fragment>
    );
  }
}

export default withWidth()(Logs);
