import React from 'react';
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import Grid from "@material-ui/core/Grid";
import { showResponse } from "../../utils/fetchUtils";


const Selector = ({
    classes,
    defaultValue,
    defaultText,
    values,
    currentValue,
    onChange,
    kind
  }) => (
  <FormControl className={classes.logsControl}>
    <InputLabel shrink>{kind}</InputLabel>
    <Select
      value={currentValue}
      onChange={e => onChange(e.target.value)}
      displayEmpty
    >
      {defaultValue !== undefined ? (
        <MenuItem value={defaultValue}>
          <em>{defaultText}</em>
        </MenuItem>
      ) : (
          ""
        )}
      {values.map(a => (
        <MenuItem value={a.port}>{a.title}</MenuItem>
      ))}
    </Select>
  </FormControl>
);

class ServerList extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            servers: []
        }
    }

    componentDidMount() {
        this.load()
    }

    async load() 
    {
      return fetch(`${process.env.REACT_APP_API_URL}get_instances`)
          .then(response => showResponse(response, "get_instances", false))
          .then(data => {
            if (data.result) this.setState({ servers: data.result })
          })
          .catch(error => toast.error("Unable to connect to API " + error));
    }

    getLocation(servers)
    {
      if (servers && servers.length)
      {
        for (const key in servers)
        {
          if (window.location.port === servers[key].port) return servers[key].port;
        }
        return servers[0].port;
      }
      return false;
    }

    onClick(port)
    {
      if (port)
      {
        const parts = window.location.href.split(':');

        window.location.href = parts[0] + ':' + parts[1] + ':' + port + window.location.pathname + window.location.hash;
      }
      return false;
    }

    render() {
        const { servers } = this.state
        const { classes } = this.props

        if (servers.length > 1)
        {
          return (
              <React.Fragment>
                  <Grid item className={classes.serverList}>
                      <Selector
                          classes={classes}
                          values={servers}
                          onChange={value => this.onClick(value)}
                          currentValue={this.getLocation(servers)}
                          kind="Switch Server"
                      />
                  </Grid>
              </React.Fragment>
          )
        }
        else return ("")
    }
}
export default ServerList;