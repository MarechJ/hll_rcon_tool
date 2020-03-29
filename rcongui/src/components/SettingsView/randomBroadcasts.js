import React from 'react';
import { toast } from "react-toastify"
import "react-toastify/dist/ReactToastify.css";
import { showResponse } from "../../utils/fetchUtils";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import Grid from "@material-ui/core/Grid";

let active = false;

fetch(`${process.env.REACT_APP_API_URL}get_randomMessagesAvailable`)
  .then(response => showResponse(response, "get_randomMessagesAvailable"))
    .then(data => active = data.result)
      .catch(error => toast.error("Unable to connect to API " + error));

const buttons = [
  {
    name: "Sequential Order",
    value: "false"
  },
  {
    name: "Random Order",
    value: "true"
  }
];

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
            <MenuItem value={a.value}>{a.name}</MenuItem>
          ))}
        </Select>
      </FormControl>
    );

class RandomBroadcast extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
          random: false
        };
    }

    componentDidMount() {
      this.load()
    }

    async load(command) {
        return fetch(`${process.env.REACT_APP_API_URL}get_randomMessages`)
          .then(response => showResponse(response, command))
            .then(data => this.state.random = data.result)
            .catch(error => toast.error("Unable to connect to API " + error));
    }

    handler(value)
    {
      this.setState({ random: value })

      this.props.broadcastChange(value)
    }

    render() {
        if (!active) return null;

        const { classes, width } = this.props;

        const {
          random
        } = this.state;

        return (
            <React.Fragment>
                <Grid item className={classes.paper} md={12} xs={12}>
                    <Selector
                        classes={classes}
                        values={buttons}
                        onChange={value => 
                          this.handler(value)
                        }
                        currentValue={random}
                        kind="Broadcast Messages are running in "
                    />
                </Grid>
            </React.Fragment>
        )
    }
}

export default RandomBroadcast;