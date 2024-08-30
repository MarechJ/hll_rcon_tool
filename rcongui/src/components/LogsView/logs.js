import React from "react";
import {
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import Select from "@mui/material/Select";
import Grid from "@mui/material/Grid";
import { Button, IconButton, Switch } from "@mui/material";
import Autocomplete from '@mui/material/Autocomplete';
import TextField from "@mui/material/TextField";
import RefreshIcon from "@mui/icons-material/Refresh";
import Paper from "@mui/material/Paper";
import moment from "moment";
import AutoRefreshLine from "../autoRefreshLine";
import ListItemText from "@mui/material/ListItemText";
import FullscreenIcon from "@mui/icons-material/Fullscreen";
import FullscreenExitIcon from "@mui/icons-material/FullscreenExit";

// FIXME checkout https://mui.com/components/use-media-query/#migrating-from-withwidth
const withWidth = () => (WrappedComponent) => (props) => <WrappedComponent {...props} width="xs" />;

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
    } else if (action.toLowerCase().includes("admin")) {
      return classes.logsAdmin;
    } else if (action.toLowerCase().includes("tk")) {
      return classes.logsTK;
    } else if (action.toLowerCase().includes("match")) {
      return classes.logsMatch;
    } else if (action.toLowerCase().includes("vote")) {
      return classes.logsVote;
    } else
      switch (action.toLowerCase()) {
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
      }
  }
  return classes.logs;
};

const Selector = ({
  defaultValue,
  defaultText,
  values,
  currentValue,
  onChange,
  kind,
  multiple,
}) => (
  <FormControl >
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
        ? localStorage.getItem("logs_highlight_logs") === 'true'
        : false,
    };

    this.loadLogs = this.loadLogs.bind(this);
    this.setActionFilter = this.setActionFilter.bind(this);
    this.setActionsFilterInclusivity =
      this.setActionsFilterInclusivity.bind(this);
    this.setLimit = this.setLimit.bind(this);
    this.setHighlightLogs = this.setHighlightLogs.bind(this);
  }

  componentDidMount() {
    setTimeout(() => {
      this.loadLogs();
    }, 1000);
  }

  loadLogs() {
    const { actionsFilter, playersFilter, limit, inclusiveFilter } = this.state;
    return postData(`${process.env.REACT_APP_API_URL}get_recent_logs`, {
      end: parseInt(limit),
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

  setHighlightLogs(highlightLogs) {
    this.setState({ highlightLogs });
    localStorage.setItem("logs_highlight_logs", highlightLogs);
  }

  render() {
    const { isFullScreen, onFullScreen } = this.props;
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
      (<React.Fragment>
        <Grid container justifyContent="flex-start">
          <Grid
            item
            xs={12}
          >
            <h1 >
              Logs view{" "}
              <IconButton onClick={onFullScreen} size="large">
                {isFullScreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
              </IconButton>
              <FormControlLabel
                control={
                  <Switch
                    checked={highlightLogs}
                    onChange={(e) => this.setHighlightLogs(e.target.checked)}
                    color="primary"
                  />
                }
                label="Highlight Logs"
                labelPlacement="top"
              />
            </h1>
            <ListItemText secondary="30s auto refresh" />
            <AutoRefreshLine
              
              intervalFunction={this.loadLogs}
              execEveryMs={30000}
              statusRefreshIntervalMs={500}
            />
          </Grid>
        </Grid>
        <Grid container justifyContent="space-around" >
          <Grid  item xs={12} sm={12} md={12} lg={2}>
            <Selector
              values={limitOptions}
              onChange={this.setLimit}
              currentValue={limit}
              kind="Show last N lines"
            />
          </Grid>
          <Grid  item xs={12} sm={12} md={12} lg={2}>
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
          <Grid  item xs={12} sm={12} md={12} lg={3}>
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
                  
                  {...params}
                  variant="outlined"
                  label="Filter by type"
                />
              )}
            />
          </Grid>
          <Grid  item xs={12} sm={12} md={12} lg={4}>
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
                  
                  {...params}
                  variant="outlined"
                  label="Filter by player"
                />
              )}
            />
          </Grid>
          <Grid  item xs={12} sm={12} md={12} lg={1}>
            <Button
              
              disableElevation
              size="large"
              variant="outlined"
              onClick={this.loadLogs}
            >
              <RefreshIcon />
            </Button>
          </Grid>
        </Grid>
        <Grid container justifyContent="center" alignItems="center">
          <Grid item  xs={12}>
            <Paper >
              {logs.map((l) => (
                <pre
                  key={l.raw}
                >
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
      </React.Fragment>)
    );
  }
}

export default withWidth()(Logs);
