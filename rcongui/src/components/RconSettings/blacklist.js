import React from 'react'
import {
    Grid, Button, TextField, Tooltip
} from "@material-ui/core"
import { showResponse, postData, get, handle_http_errors } from '../../utils/fetchUtils'
import Autocomplete from "@material-ui/lab/Autocomplete";
import { getSharedMessages } from "../../utils/fetchUtils";
import TextHistory from "../textHistory";

class Blacklist extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      steam_id: "",
      name: "",
      reason: "",
      sharedMessages: [],
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
      .catch(handle_http_errors)
  }

  componentDidMount() {
    getSharedMessages("punitions").then((data) =>
    this.setState({ sharedMessages: data })
  );
  }

  render() {
    const { steam_id, name, reason, sharedMessages } = this.state
    const { classes } = this.props
    const textHistory = new TextHistory("punitions");
    
    return (
      <Grid container spacing={1} justify="space-between">
        <Grid item xs={6} md={3}>
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
        <Grid item xs={6} md={3}>
            <TextField
              id="name"
              label="Player name"
              helperText="Optional"
              value={name}
              fullWidth
              onChange={(e) => this.setState({ name: e.target.value })}
            />
        </Grid>
        <Grid item xs={12} md={4}>
        <Autocomplete
            freeSolo
            fullWidth
            options={sharedMessages.concat(textHistory.getTexts())}
            inputValue={reason}
            required
            onInputChange={(e, value) => this.setState({ reason: value })}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Reason"
                helperText="Required"
              />
            )}
          />
        </Grid>
        <Grid item xs={12} md={2} className={`${classes.padding} ${classes.margin}`}>
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
