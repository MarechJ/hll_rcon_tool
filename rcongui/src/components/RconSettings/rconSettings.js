import React from 'react'
import {
    Grid, Typography, Button, TextField
} from "@material-ui/core"
import { range } from "lodash/util"
import { showResponse, postData, get, handle_http_errors } from '../../utils/fetchUtils'
import Blacklist from "./blacklist"
import { toast } from "react-toastify"
import _ from 'lodash'
import LinearProgress from "@material-ui/core/LinearProgress"
import Padlock from '../../components/SettingsView/padlock'
import WarningIcon from '@material-ui/icons/Warning';
import TextHistoryManager, { SelectNameSpace } from './textHistoryManager'
import TextHistory from '../textHistory'

class RconSettings extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            broadcastMessages: [],
            standardMessages: [],
            standardMessagesType: 'punitions',
            randomized: false,
            enabled: false,
        }

        this.loadBroadcastsSettings = this.loadBroadcastsSettings.bind(this)
        this.validate_messages = this.validate_messages.bind(this)
        this.saveBroadCastMessages = this.saveBroadCastMessages.bind(this)
        this.loadStandardMessages = this.loadStandardMessages.bind(this)
        this.saveStandardMessages = this.saveStandardMessages.bind(this)
        this.clearCache = this.clearCache.bind(this)
    }

    async loadBroadcastsSettings() {
        return get(`get_auto_broadcasts_config`)
            .then((res) => showResponse(res, "get_auto_broadcasts_config", false))
            .then(data => !data.failed && this.setState({
                broadcastMessages: data.result.messages,
                randomized: data.result.randomized,
                enabled: data.result.enabled
            }))
            .catch(handle_http_errors)
    }

    async saveBroadcastsSettings(data) {
        return postData(`${process.env.REACT_APP_API_URL}set_auto_broadcasts_config`,
            data
        )
            .then((res) => showResponse(res, "set_auto_broadcasts_config", true))
            .then(res => !res.failed && this.setState(data))
            .catch(handle_http_errors)
    }

    async loadStandardMessages() {
        return get(`get_standard_messages?message_type=${this.state.standardMessagesType}`)
            .then((res) => showResponse(res, "get_standard_messages", false))
            .then(data => !data.failed && this.setState({
                standardMessages: data.result
            }))
            .catch(handle_http_errors)
    }

    async saveStandardMessages() {
        return postData(`${process.env.REACT_APP_API_URL}set_standard_messages`,
            {message_type: this.state.standardMessagesType, messages: this.state.standardMessages}
        )
            .then((res) => showResponse(res, "set_standard_messages", true))
            .then(this.loadStandardMessages)
            .catch(handle_http_errors)
    }

    async clearCache() {
        return postData(`${process.env.REACT_APP_API_URL}clear_cache`, {})
            .then((res) => showResponse(res, "clear_cache", true))
            .catch(handle_http_errors)
    }

    validate_messages() {
        let hasErrors = false
        _.forEach(this.state.broadcastMessages, m => {
            const split = _.split(m, ' ')

            if (_.isNaN(_.toNumber(split[0]))) {
                toast.error(`Invalid line, must start with number of seconds: ${m}`)
                hasErrors = true
            }
        })
        return !hasErrors
    }

    saveBroadCastMessages() {
        if (this.validate_messages()) {
            this.saveBroadcastsSettings({ messages: this.state.broadcastMessages })
        }
    }

    componentDidMount() {
        this.loadBroadcastsSettings()
        this.loadStandardMessages()
    }

    render() {
        const { broadcastMessages, standardMessages, standardMessagesType, enabled, randomized } = this.state
        const { classes } = this.props

        return (
            <Grid container className={classes.paper} spacing={3}>
                <Grid item xs={12}>
                    <h2>Advanced RCON settings</h2>
                </Grid>
                <Grid item xs={12}>
                    <Grid container justify="space-evenly">
                        <Grid item>
                            <Padlock handleChange={v => this.saveBroadcastsSettings({ enabled: v })} checked={enabled} label="Auto broadcast enabled" />
                        </Grid>
                        <Grid item>
                            <Padlock handleChange={v => this.saveBroadcastsSettings({ randomized: v })} checked={randomized} label="Randomized messages" />
                        </Grid>
                    </Grid>
                </Grid>
                <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Auto broadcast messages"
                        multiline
                        rows={8}
                        value={_.join(broadcastMessages.map(m => m.replace(/\n/g, '\\n')), '\n')}
                        onChange={(e) => this.setState({ broadcastMessages: _.split(e.target.value, '\n') })}
                        placeholder="Insert your messages here, one per line, with format: <number of seconds to display> <a message (write: \n if you want a line return)>"
                        variant="outlined"
                        helperText="You can use the following variables in the text (nextmap, maprotation, servername, onlineadmins, admins, owners, seniors, juniors, vips, randomvip, ingame_mods, online_mods) using the following syntax: 60 Welcome to {servername}. The next map is {nextmap}."
                    />
                </Grid>
                <Grid item xs={12}>
                    <Button fullWidth onClick={this.saveBroadCastMessages} variant="outlined">Save auto broadcast messages</Button>
                </Grid>
                <Grid container spacing={1} alignContent="center" justify="center" alignItems="center" className={classes.root}>
                    <Grid item xs={12} className={`${classes.padding} ${classes.margin}`}>
                        <TextHistoryManager classes={classes} />
                    </Grid>
                </Grid>
                <Grid item xs={12} className={classes.padding}>
                    <Typography variant="h6">Manage shared standard messages</Typography>
                </Grid>
                <Grid item xs={12} className={classes.padding}>
                    <SelectNameSpace value={standardMessagesType} handleChange={v => this.setState({standardMessagesType: v}, this.loadStandardMessages)} values={['punitions', 'welcome', 'broadcast']} />
                </Grid>
                <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Shared standard messages"
                        multiline
                        rows={8}
                        value={_.join(standardMessages.map(m => m.replace(/\n/g, '\\n')), '\n')}
                        onChange={(e) => this.setState({ standardMessages: _.split(e.target.value, '\n') })}
                        placeholder="Set one message per line. If you want a line return in one of the message write: \n"
                        variant="outlined"
                        helperText="Set one message per line. If you want a line return in one of the message write: \n"
                    />
                </Grid>
                <Grid item xs={12}>
                    <Button fullWidth onClick={this.saveStandardMessages} variant="outlined">Save shared messages</Button>
                </Grid>
                <Grid item className={classes.paddingTop} justify="center" xs={12}>
                  <Typography variant="h5">
                      Blacklist player by Steam ID
                  </Typography>
                </Grid>
                <Blacklist
                    classes={classes}
                />
                <Grid item className={classes.paddingTop} justify="center" xs={12}>
                    <Typography variant="h5">
                        More options 
                    </Typography>
                </Grid>
                <Grid item xs={12} className={`${classes.padding} ${classes.margin}`} alignContent="center" justify="center" alignItems="center" className={classes.root}>
                    <Button color="secondary" variant="outlined" onClick={this.clearCache}>Clear application cache</Button>
                </Grid>
            </Grid>
        )
    }
}


export default RconSettings
