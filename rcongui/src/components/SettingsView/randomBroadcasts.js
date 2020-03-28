import React from 'react';
import { toast } from "react-toastify"
import "react-toastify/dist/ReactToastify.css";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import Grid from "@material-ui/core/Grid";

let active = true;

fetch(`${process.env.REACT_APP_API_URL}get_randomMessagesActive`)
        .then(data => console.log("Messges Active: " + data))
        .catch(error => toast.error("Unable to connect to API " + error));

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
        super(props)
    }

    async load(command) {
        return fetch(`${process.env.REACT_APP_API_URL}get_randomMessages`)
            .then(data => console.log("Random Messges: " + data))
            .catch(error => toast.error("Unable to connect to API " + error));
    }

    render() {
        if (!active) return null;

        const { classes, width } = this.props;
  
        const button = {
            "values": [
                {
                    name: "Random Order",
                    value: "on"
                },
                {
                    name: "Sequential Order",
                    value: "off"
                }
            ]
        };

        let current = button.values[0].value;
        
        if (!this.data)
            current = button.values[1].value;

        return (
            <React.Fragment>
                <Grid item className={classes.paper} md={12} xs={12}>
                    <Selector
                        classes={classes}
                        values={button.values}
                        onChange={value =>
                            this.props.broadcastChange(value)
                        }
                        currentValue={current}
                        kind="Toggle Broadcast message order"
                    />
                </Grid>
            </React.Fragment>
        )
    }
}

export default RandomBroadcast;