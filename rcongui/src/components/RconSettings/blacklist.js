import React from 'react'
import {
    Grid, Button, TextField, Tooltip, Checkbox, FormControlLabel
} from "@material-ui/core"
import Autocomplete from '@material-ui/lab/Autocomplete'
import TextHistory from '../textHistory'

class Blacklist extends React.Component {

  constructor(props) {
    super(props)
  }

  render() {
    const { classes, submitBlacklistPlayer, steam_id, name, reason, save_message, handleChange } = this.props 
    const textHistory = new TextHistory('punitions')

    return (
      <Grid container className={classes.paper} spacing={1}>
        <Grid item xs={3}>
            <TextField
              id="steam-id"
              value={steam_id}
              label="Steam ID"
              helperText="Required"
              required
              fullWidth
              onChange={(e) => handleChange(e.target.value, this.props.name, this.props.reason, this.props.save_message)}
            />
        </Grid>
        <Grid item xs={4} spacing={1}>
          <Autocomplete
            value={reason}
            freeSolo
            fullWidth
            options={textHistory.getTexts()}
            onInputChange={(e, value) => handleChange(this.props.steam_id, this.props.name, value, this.props.save_message)}
            renderInput={(params) => (
              <TextField {...params} label="Reason" helperText="A message is mandatory" />
            )}
          />
        </Grid>
        <Grid item xs={3} spacing={1}>
          <TextField
            id="name"
            value={name}
            label="Player name"
            helperText="Optional"
            fullWidth
            onChange={(e) => handleChange(this.props.steam_id, e.target.value, this.props.reason, this.props.save_message)}
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
                 }
               }
            >
                 Blacklist
            </Button>
          </Grid>
        </Tooltip>
      </Grid>
    )
  }
}

export default Blacklist
