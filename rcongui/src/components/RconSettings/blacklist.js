import React from 'react'
import {
    Grid, Button, TextField, Tooltip, Checkbox, FormControlLabel
} from "@material-ui/core"
import Autocomplete from '@material-ui/lab/Autocomplete'
import TextHistory from '../textHistory'

class Blacklist extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      steam_id: "",
      name: "",
      reason: "",
      saveMessage: true
    }

    this.onChange = this.onChange.bind(this);
  }

  onChange(e, value) {
    e.preventDefault();
    this.setState({ reason: value });
  }

  render() {
    const { steam_id, name, reason, saveMessage } = this.state
    const { classes, submitBlacklistPlayer } = this.props 
    const textHistory = new TextHistory('punitions')

    return (
      <Grid container className={classes.paper} spacing={1}>
        <Grid item xs={3}>
            <TextField
              id="steam-id"
              label="Steam ID"
              helperText="Required"
              value={steam_id}
              required
              fullWidth
              onChange={(e) => this.setState({ steam_id: e.target.value })}
            />
        </Grid>
        <Grid item xs={4} spacing={1}>
          <Autocomplete
            freeSolo
            fullWidth
            options={textHistory.getTexts()}
            inputValue={reason}
            onInputChange={(e, value) => this.onChange(e, value)}
            renderInput={(params) => (
              <TextField {...params} label="Reason" helperText="A message is mandatory" />
            )}
          />
        </Grid>
        <Grid item xs={3} spacing={1}>
            <TextField
              id="name"
              label="Player name"
              helperText="Optional"
              value={name}
              fullWidth
              onChange={(e) => this.setState({ name: e.target.value })}
            />
        </Grid>
            <Tooltip fullWidth title="Blacklisted players will instantly be banned when entering the server." arrow>
                <Grid item xs={2} spacing={1} className={`${classes.padding} ${classes.margin}`} justify="center" alignContent="center">
                    <Button 
                       color="secondary"
                       variant="outlined"
                       disabled={!steam_id || !reason }
                       onClick={
                         () => { 
                           submitBlacklistPlayer(steam_id, name, reason)
                             .then((res) => !res.failed && this.setState({ steam_id: "", name: "", reason: "" }))
                         } 
                       }>
                         Blacklist
                    </Button>
              </Grid>
          </Tooltip>
      </Grid>
    )
  }
}

export default Blacklist
