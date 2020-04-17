import React from 'react'
import {
    Grid, Typography, Button, TextField
} from "@material-ui/core"
import { range } from "lodash/util"
import { showResponse, postData } from '../../utils/fetchUtils'
import { toast } from "react-toastify"
import _ from 'lodash'
import LinearProgress from "@material-ui/core/LinearProgress"
import Padlock from '../../components/SettingsView/padlock'

class RconSettings extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            messages: [],
            randomized: false,
            enabled: false
        }

        this.loadBroadcastsSettings = this.loadBroadcastsSettings.bind(this)
    }

    async loadBroadcastsSettings() {
        return fetch(`${process.env.REACT_APP_API_URL}get_auto_broadcasts_config`)
            .then((res) => showResponse(res, "get_auto_broadcasts_config", false))
            .then(data => this.setState({
                message: data.result.messages,
                randomized: data.result.randomized,
                enabled: data.result.enabled
            }))
    }

    componentDidMount() {
        this.loadBroadcastsSettings()
    }

    render() {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12}>
                    <h2>Advanced RCON settings</h2>
                </Grid>
                <Grid item xs={12}>
                    <Grid container justify="space-evenly">
                        <Grid item>
                            <Padlock checked={false} label="Auto broadcast enabled" />
                        </Grid>
                        <Grid item>
                            <Padlock checked={false} label="Randomized messages" />
                        </Grid>
                    </Grid>
                </Grid>

                <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Auto broadcast messages"
                        multiline
                        rows={8}
                        placeholder="Insert your messages here, one per line, with format: <number of seconds to display> <a message>"
                        variant="outlined"
                        helperText="You can use the following variables in the text (nextmap, maprotation, servername) using the followin syntax: 60 Welcome to {servername}. The next map is {nextmap}."
                    />
                </Grid>
                <Grid item xs={12}>
                    <Button fullWidth variant="outlined">Save messages</Button>
                </Grid>
            </Grid>
        )
    }
}


export default RconSettings