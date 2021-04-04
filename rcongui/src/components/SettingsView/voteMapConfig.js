import { Button, FormControl, Grid, InputLabel, NativeSelect, TextField, Typography } from '@material-ui/core'
import React from 'react'
import { Map, fromJS, List } from 'immutable'
import {
    showResponse,
    postData,
    get,
    handle_http_errors,
    sendAction,
} from "../../utils/fetchUtils";
import Padlock from './padlock';

const VoteMapConfig = () => {
    const [config, setConfig] = React.useState(new Map())
    const [status, setStatus] = React.useState(new Map())

    const saveConfig = (kv) => postData(`${process.env.REACT_APP_API_URL}set_votemap_config`, kv)
        .then(res => showResponse(res, "set_votemap_config", true))
        .then(data => data.failed ? "" : setConfig(fromJS(data.result)))
        .catch(handle_http_errors)

    const loadData = () => {
        get('get_votemap_status')
            .then(res => showResponse(res, "get_votemap_status", false))
            .then(data => data.failed ? "" : setStatus(fromJS(data.result)))
            .catch(handle_http_errors)
        get("get_votemap_config")
            .then(res => showResponse(res, "get_votemap_config", false))
            .then(data => data.failed ? "" : setConfig(fromJS(data.result)))
            .catch(handle_http_errors)
    }

    const resetVotes = () => (
        postData(`${process.env.REACT_APP_API_URL}reset_votemap_state`)
        .then(res => showResponse(res, "reset_votemap_state", true))
        .then(res => res.failed ? "" : setStatus(fromJS(res.result)))
        .catch(handle_http_errors)
    )
    
    React.useEffect(() => {
        loadData();
        const handle = setInterval(loadData, 60000)
        return () => clearInterval(handle)
    }, [])

    return <Grid container spacing={2} justify="flex-start" alignContent="center" alignItems="center" >
        <Grid item xs={12}>
            <Padlock label="Next Map Vote Enabled" checked={config.get("vote_enabled", false)} handleChange={(v) => saveConfig({ vote_enabled: v })} />
        </Grid>
        <Grid item>
            <TextField 
                label="Text to explain how to vote"
                helperText="The text shown in some preformated broadcasts"
                value={config.get("votemap_instruction_text", "")}
                onChange={e => setConfig({ ...config, votemap_instruction_text: e.target.value })}
            />
        </Grid>
        <Grid item>
            <TextField type="number" inputProps={{ min: 2, max: 10 }}
                label="Number of options in selection"
                helperText="The amount of maps that should be offered in the vote"
                value={config.get("votemap_number_of_options", false)}
                onChange={e => saveConfig({ votemap_number_of_options: e.target.value })}
            />
        </Grid>
        <Grid item>
            <TextField type="number" inputProps={{ min: 0, max: 1, step: 0.05 }}
                label="Ratio of offensives"
                helperText="The ratio of offensive maps in the selection"
                value={config.get("votemap_ratio_of_offensives_to_offer", false)}
                onChange={e => saveConfig({ votemap_ratio_of_offensives_to_offer: e.target.value })}
            />
        </Grid>
        <Grid item> <TextField type="number" inputProps={{ min: 0, max: 6, step: 1 }}
            label="Number of recently played maps excluded"
            helperText="Exclude the last N played maps from the selection. The current map is always excluded."
            value={config.get("votemap_number_of_last_played_map_to_exclude", false)}
            onChange={e => saveConfig({ votemap_number_of_last_played_map_to_exclude: e.target.value })}
        />
        </Grid>
        <Grid item>
            <Padlock label="Consider offensive map being the same as warfare when excluding"
                checked={config.get("votemap_consider_offensive_as_same_map", false)}
                handleChange={(v) => saveConfig({ votemap_consider_offensive_as_same_map: v })} />
        </Grid>

        <Grid item>
            <Padlock label="Allow consecutive offensive map"
                checked={config.get("votemap_allow_consecutive_offensives", false)}
                handleChange={(v) => saveConfig({ votemap_allow_consecutive_offensives: v })} />
        </Grid>

        <Grid item>
            <Padlock label="Allow consecutive offensive where a team would play defense twice in a row. E.g off_ger followed by off_us"
                checked={config.get("votemap_allow_consecutive_offensives_of_opposite_side", false)}
                handleChange={(v) => saveConfig({ votemap_allow_consecutive_offensives_of_opposite_side: v })} />
        </Grid>

        <Grid item>
            <FormControl>
                <InputLabel>Default map method (when no votes)</InputLabel>
                <NativeSelect
                    value={config.get("votemap_default_method", "")}
                    onChange={e => saveConfig({ votemap_default_method: e.target.value })} >
                    <option value="least_played_from_suggestions">Pick least played map from suggestions</option>
                    <option value="least_played_from_all_map">Pick least played map from all maps</option>
                    <option value="random_from_suggestions">Pick randomly from suggestions</option>
                    <option value="random_from_all_maps">Pick randomly from all maps</option>
                </NativeSelect>
            </FormControl>
        </Grid>
        <Grid item>
            <Padlock label="Allow default map to be an offensive"
                checked={config.get("votemap_allow_default_to_offsensive", false)}
                handleChange={(v) => saveConfig({ votemap_allow_default_to_offsensive: v })} />
        </Grid>
        <Grid item xs={12}>
            <Grid container justify="flex-start" alignContent="stretch" alignItems="stretch" orientation="column">
                <Grid item xs={12}>
                    <Typography variant="h6">Current vote status</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Typography variant="body1">Votes:</Typography>
                    <pre>
                        {status.get("votes", new Map()).entrySeq().map(
                            (o) => `${o[0]}: ${o[1]}\n`
                        )}
                    </pre>
                </Grid>
                <Grid item xs={6} sm={4}>
                    <Typography variant="body1">Map selection:</Typography>
                    <pre>
                        {status.get("selection", new List()).map(
                            (v) => `${v}\n`
                        )}</pre>
                </Grid>
                <Grid item xs={6} sm={4}>
                    <Typography variant="body1">Results:</Typography>
                    <pre>
                        {status.get("results", new Map()).get("winning_maps", new List()).map(
                            (o) => `${o.get(0)}: ${o.get(1)} vote(s)\n`
                        )}</pre>
                </Grid>
                <Grid xs={12}><Button variant="outlined" color="secondary" onClick={() => {if (window.confirm("Are you sure?") === true) { resetVotes() }}} >RESET SELECTION & VOTES</Button></Grid>
            </Grid>
            
        </Grid>

    </Grid>
}

export default VoteMapConfig