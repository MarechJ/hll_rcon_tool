import React from "react";
import { Paper } from "material-ui";
import { toast } from "react-toastify";
import { postData, showResponse } from "../../utils/fetchUtils";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import Grid from "@material-ui/core/Grid";
import { Button } from "@material-ui/core";

class Logs extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      logs: [],
      actions: [],
      players: [],
      actionsFilter: "",
      minutes: 60
    };

    this.loadLogs = this.loadLogs.bind(this);
  }
  componentDidMount() {
    setTimeout(() => {
      this.loadLogs();
    }, 1000);
  }

  loadLogs() {
    const { actionsFilter, minutes} = this.state;
    let qs = `?since_min_ago=${minutes}`;
    if (actionsFilter !== "") {
      qs += `&filter_action=${actionsFilter}`;
    }
    return fetch(`${process.env.REACT_APP_API_URL}get_structured_logs${qs}`)
      .then(response => showResponse(response, "get_logs"))
      .then(data =>
        this.setState({
          logs: data.result.logs,
          actions: data.result.actions,
          players: data.result.players
        })
      )
      .catch(error => toast.error("Unable to connect to API " + error));
  }

  render() {
    const { classes } = this.props;
    const { logs, players, actions, actionsFilter } = this.state;
    return (
    <React.Fragment>
      <Grid container justify="flex-end" alignItems="flex-end">
          <Grid item xs={6}>
        <FormControl classes={classes.marginLeft} style={{minWidth: "100px"}}>
          <InputLabel shrink>Filter by type</InputLabel>
          <Select
            value={actionsFilter}
            onChange={e =>
              this.setState({ actionsFilter: e.target.value }, this.loadLogs)
            }
            displayEmpty
          >
            <MenuItem value="">
              <em>ALL</em>
            </MenuItem>
            {actions.map(a => (
              <MenuItem value={a}>{a}</MenuItem>
            ))}
          </Select>
        </FormControl>
        </Grid>
        <Grid item xs={6}>
        <Button disableElevation variant="outlined" onClick={this.loadLogs}>
          Reload
        </Button>
        </Grid>
        </Grid>
        <Grid container justify="center" alignItems="center">
        <Grid xs={10}>
        <pre classes={classes.marginLeft} style={{ textAlign: "left" }}>
          {logs.map(l => (
            <React.Fragment>{l.raw + "\n"}</React.Fragment>
          ))}
        </pre>
        </Grid>
      </Grid>
      </React.Fragment>
    );
  }
}

export default Logs;
