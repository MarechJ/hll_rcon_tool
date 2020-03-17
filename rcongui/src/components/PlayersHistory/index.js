/* eslint-disable no-use-before-define */
import React from 'react';
import useAutocomplete from '@material-ui/lab/useAutocomplete';
import { makeStyles } from '@material-ui/core/styles';
import { postData, showResponse } from "../../utils/fetchUtils";
import { toast } from "react-toastify";
import { join, each, reduce, get } from 'lodash'
import Autocomplete from "@material-ui/lab/Autocomplete";
import Pagination from '@material-ui/lab/Pagination';
import { Paper, Icon, Grid, Chip, Divider, Popover, Badge, Button, TextField, FormControl, InputLabel, MenuItem, Select } from '@material-ui/core'
import moment from 'moment'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSkullCrossbones } from '@fortawesome/free-solid-svg-icons'
import { ReasonDialog } from "../PlayerView/playerActions";
import RefreshIcon from '@material-ui/icons/Refresh';



const show_names = (names) => (
    join(names, ' · ')
)

const WithPopver = ({ classes, popoverContent, children }) => {
    const [anchorEl, setAnchorEl] = React.useState(null);

    const handlePopoverOpen = event => {
        setAnchorEl(event.currentTarget);
    };

    const handlePopoverClose = () => {
        setAnchorEl(null);
    };

    const open = Boolean(anchorEl);

    return (
        <React.Fragment>
            <div onMouseEnter={handlePopoverOpen}
                onMouseLeave={handlePopoverClose}>
                {children}
            </div>
            <Popover
                id="mouse-over-popover"
                className={classes.popover}
                classes={{
                    paper: classes.paper,
                }}
                open={open}
                anchorEl={anchorEl}
                anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'left',
                }}
                transformOrigin={{
                    vertical: 'top',
                    horizontal: 'left',
                }}
                onClose={handlePopoverClose}
                disableRestoreFocus
            >
                {popoverContent}
            </Popover>
        </React.Fragment>
    );
}

const PlayerItem = ({ classes, names, steamId64, firstSeen, lastSeen, blacklisted, onBlacklist, onUnBlacklist, compact = true }) => {
    const now = moment()
    const last_seen = moment(lastSeen)
    const first_seen = moment(firstSeen)
    const extraneous = compact ? { display: 'none' } : {}
    const headerClasses = compact ? classes.noPaddingMargin : classes.noPaddingMarginBottom

    return <Grid container>
        <Grid item xs={12}>
            <Paper>
                <Grid container justify="flex-start" alignItems="center" className={`${classes.doublePadding} ${classes.paddingBottom}`}>
                    <Grid item xs={8} sm={7}>
                        <Grid container alignContent="flex-start">
                            <Grid item xs={12}>
                                <h4 style={{ display: "flex" }} className={`${classes.noPaddingMargin} ${classes.ellipsis}`}>
                                    {names}
                                </h4>
                            </Grid>
                            <Grid item xs={12}>
                                <small style={{ display: "flex" }}>{steamId64}</small>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={4} sm={5}>
                        {blacklisted
                            ? <Button variant="outlined" onClick={onUnBlacklist}>Unblacklist</Button>
                            : <Button variant="outlined" color="secondary" onClick={onBlacklist} >Blacklist <FontAwesomeIcon icon={faSkullCrossbones} /></Button>
                        }
                    </Grid>
                </Grid>
                <Grid container justify="space-between" spacing={0} style={extraneous} className={classes.padding}>
                    <Grid item xs={6}>
                        <WithPopver classes={classes} popoverContent={<p>{first_seen.format('LLLL')}</p>}>
                            <small>First seen {moment.duration(now.diff(first_seen)).humanize()} ago</small>
                        </WithPopver>
                    </Grid>
                    <Grid item xs={6}>
                        <WithPopver classes={classes} popoverContent={<p>{last_seen.format('LLLL')}</p>}>
                            <small>Last seen {moment.duration(now.diff(last_seen)).humanize()} ago</small>
                        </WithPopver>
                    </Grid>
                    <Grid item xs={6}>
                        <small># Punish: N/A </small>
                    </Grid>
                    <Grid item xs={6}>
                        <small># Kick: N/A </small>
                    </Grid>
                    <Grid item xs={6}>
                        <small># Tempban: N/A </small>
                    </Grid>
                    <Grid item xs={6}>
                        <small># Permaban: N/A </small>
                    </Grid>
                </Grid>
            </Paper>
        </Grid>
    </Grid>
}

const MyPagination = ({ classes, pageSize, total, page, setPage }) => (

    <Pagination count={Math.ceil(total / pageSize)} page={page} onChange={(e, val) => setPage(val)}
        variant="outlined" color="default" showFirstButton showLastButton className={classes.pagination} />

)


const FilterPlayer = ({ classes, playersHistory, pageSize, total, page, setPageSize, setPage, onUnBlacklist, onBlacklist, onRefresh, namesIndex }) => {
    const {
        getRootProps,
        getInputLabelProps,
        getInputProps,
        getListboxProps,
        getOptionProps,
        groupedOptions,
    } = useAutocomplete({
        forcePopupIcon: true,
        freeSolo: true,
        selectOnFocus: true,
        blurOnSelect: false,
        disableOpenOnFocus: true,
        disableCloseOnSelect: true,
        disableClearable: true,
        disableListWrap: true,
        disableRestoreFocus: true,
        disablePortal: true,
        autoSelect: true, 
        debug: true,
        options: namesIndex,
        getOptionLabel: option => option.names ? option.names : option,
    });

    const [doConfirmPlayer, setDoConfirmPlayer] = React.useState(false)
    const playerList = groupedOptions.length > 0 ? groupedOptions : namesIndex
 
    return (
        <div>
            <Grid container {...getRootProps()} alignContent="flex-start" alignItems="center" spacing={2}>
                <Grid item xs={12} md={6}>
                    <TextField fullWidth inputProps={{ ...getInputProps() }} label="Filter current selection" InputLabelProps={{ shrink: true }} />
                </Grid>
                <Grid item xs={12} md={5}>
                    <FormControl fullWidth>
                        <InputLabel >Page size</InputLabel>
                        <Select
                            value={pageSize}
                            onChange={e => setPageSize(e.target.value)}
                        >
                            <MenuItem value={10}>10</MenuItem>
                            <MenuItem value={20}>20</MenuItem>
                            <MenuItem value={30}>30</MenuItem>
                            <MenuItem value={40}>40</MenuItem>
                            <MenuItem value={50}>50</MenuItem>
                            <MenuItem value={100}>100</MenuItem>
                            <MenuItem value={200}>200</MenuItem>
                            <MenuItem value={500}>500</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={12} md={1}>
                    <Button variant="outlined" onClick={onRefresh}><RefreshIcon /></Button>
                </Grid>
                <Grid item xs={12}>
                    <MyPagination classes={classes} pageSize={pageSize} page={page} setPage={setPage} total={total} />
                </Grid>
            </Grid>
            <Grid container {...getListboxProps()} spacing={2}>
                {playerList.map(nameIndex => {
                    const player = playersHistory[nameIndex.idx]
                    return <Grid key={player.steam_id_64} /*style={{display: displayMap[player.steam_id_64] ? "block": "none"}}*/ item xs={12} sm={6} md={4} lg={3} xl={2}>
                        <PlayerItem
                            key={player.steam_id_64}
                            classes={classes}
                            names={show_names(player.names)}
                            steamId64={player.steam_id_64}
                            firstSeen={player.first_seen_timestamp_ms}
                            lastSeen={player.last_seen_timestamp_ms}
                            compact={false}
                            blacklisted={player.blacklisted}
                            onBlacklist={() => setDoConfirmPlayer({ player: player.steam_id_64, actionType: "blacklist" })}
                            onUnBlacklist={() => onUnBlacklist(player.steam_id_64)}
                        />
                    </Grid>
                })}
                <Grid item xs={12}>
                    <MyPagination classes={classes} pageSize={pageSize} page={page} setPage={setPage} total={total} />
                </Grid>
            </Grid>
            <ReasonDialog
                open={doConfirmPlayer}
                handleClose={() => setDoConfirmPlayer(false)}
                handleConfirm={(actionType, steamId64, reason) => {
                    onBlacklist(steamId64, reason)
                    setDoConfirmPlayer(false);
                }}
            />
        </div>
    );
}


class PlayersHistory extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            playersHistory: [],
            total: 0,
            pageSize: 50,
            page: 1
        }

        this.getPlayerHistory = this.getPlayerHistory.bind(this)
        this.blacklistPlayer = this.blacklistPlayer.bind(this)
        this.unblacklistPlayer = this.unblacklistPlayer.bind(this)
    }

    getPlayerHistory() {
        const { pageSize, page } = this.state
        return fetch(`${process.env.REACT_APP_API_URL}players_history?page_size=${pageSize}&page=${page}`)
            .then(response => showResponse(response, 'player_history'))
            .then(data => {
                if (data.failed) {
                    return
                }
                this.setState({
                    playersHistory: data.result.players,
                    total: data.result.total,
                    pageSize: data.result.page_size,
                    page: data.result.page
                })
            })
            .catch(error => toast.error("Unable to connect to API " + error));
    }

    blacklistPlayer(steamId64, reason) {
        postData(`${process.env.REACT_APP_API_URL}blacklist_player`, {
            steam_id_64: steamId64,
            reason: reason
        })
            .then(response =>
                showResponse(
                    response,
                    `PlayerID ${steamId64} blacklist for ${reason}`,
                    true
                )
            ).then(
                this.getPlayerHistory()
            )
    }

    unblacklistPlayer(steamId64) {
        postData(`${process.env.REACT_APP_API_URL}unblacklist_player`, {
            steam_id_64: steamId64,
        })
            .then(response =>
                showResponse(
                    response,
                    `PlayerID ${steamId64} removed from blacklist`,
                    true
                )
            ).then(
                this.getPlayerHistory()
            )
    }


    componentDidMount() {
        this.getPlayerHistory()
    }

    render() {
        const { classes } = this.props
        let { playersHistory, pageSize, page, total } = this.state

        // There's a bug in the autocomplete code, if there's a boolean in the object it makes it match against
        // "false" or "true" so essentially, everything matches to "F" or "T"
        // That's why we remap the list
   
        return <Grid container className={classes.padding}>
            <Grid item xs={12}>
                <FilterPlayer
                    classes={classes}
                    playersHistory={playersHistory}
                    namesIndex={playersHistory.map((el, idx) => ({names: join(el.names, ','), idx: idx}))}
                    pageSize={pageSize}
                    setPageSize={(pageSize) => this.setState({ pageSize: pageSize }, this.getPlayerHistory)}
                    total={total}
                    page={page}
                    setPage={(page) => this.setState({ page: page }, this.getPlayerHistory)}
                    onBlacklist={this.blacklistPlayer}
                    onUnBlacklist={this.unblacklistPlayer}
                    onRefresh={this.getPlayerHistory}
                />
            </Grid>
        </Grid>
    }
}

export default PlayersHistory