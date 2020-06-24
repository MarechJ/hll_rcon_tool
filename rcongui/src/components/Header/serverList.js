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
        <MenuItem key={a.port} value={a.port}>{a.title}</MenuItem>
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

    onClick(port)
    {
      if (port)
      {
        window.location.href = `${window.location.protocol}//${window.location.hostname}:${port}${window.location.pathname}${window.location.hash}`
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
                          currentValue={window.location.port}
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