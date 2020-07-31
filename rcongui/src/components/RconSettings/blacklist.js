import React from 'react'
import {
    Grid, Typography, Button, TextField, Tooltip
} from "@material-ui/core"
import { showResponse, postData } from '../../utils/fetchUtils'

class Blacklist extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      steam_id: "",
      name: "",
      rason: "",
    }

    this.blacklistPlayer = this.blacklistPlayer.bind(this)
  }

  async blacklistPlayer() {
      return postData(`${process.env.REACT_APP_API_URL}blacklist_player`, {
        "steam_id_64": this.state.steam_id,
        "name": this.state.name,
        "reason": this.state.reason,
      })
      .then((res) => showResponse(res, "blacklist_player", true))
      .then(res => !res.failed && this.setState({ steam_id: "", name: "", reason: "" }))
  }

  componentDidMount() {
  }

  render() {
    const { steam_id, name, reason } = this.state
    const { classes } = this.props 

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
            <TextField
              id="reason"
              label="Reason"
              helperText="Required"
              value={reason}
              required
              fullWidth
              onChange={(e) => this.setState({ reason: e.target.value })}
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
        <Grid item xs={2} spacing={1} className={`${classes.padding} ${classes.margin}`} justify="center" alignContent="center">
            <Tooltip fullWidth title="Blacklisted players will instantly be banned when entering the server." arrow>
                <Button 
                        color="secondary"
                        variant="outlined"
                        disabled={steam_id == "" || reason == ""} onClick={this.blacklistPlayer}>
                    Blacklist
                </Button>
            </Tooltip>
        </Grid>
      </Grid>
    )
  }
}

export default Blacklist
