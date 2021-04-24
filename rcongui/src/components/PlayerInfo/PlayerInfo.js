import {get, handle_http_errors, showResponse} from "../../utils/fetchUtils";
import React from "react";
import {Avatar, Button, Grid, Popover} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import {ExpandMore} from "@material-ui/icons";
import moment from "moment";
import MUIDataTable from "mui-datatables";
import {withRouter} from "react-router";

const NamePopOver = ({names}) => {
    const [anchorEl, setAnchorEl] = React.useState(null);

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const open = Boolean(anchorEl);
    const id = open ? 'name-popover' : undefined;

    return (
        <Grid item>
            <Button endIcon={<ExpandMore/>} onClick={handleClick}>
                <Typography variant="h5">{names[0].name}</Typography>
            </Button>
            <Popover
                id={id}
                open={open}
                anchorEl={anchorEl}
                onClose={handleClose}
                anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'center',
                }}
                transformOrigin={{
                    vertical: 'top',
                    horizontal: 'center',
                }}
            >
                {names.map((name) => {
                    return <Typography>{name.name}</Typography>;
                })}
            </Popover>
        </Grid>
    );
}

const Punishment = ({punishments}) => {
    const [myRowPerPage, setRowPerPage] = React.useState(
        window.localStorage.getItem("punishments_row_per_page") || 50
    );
    const saveRowsPerPage = (rowPerPage) => {
        window.localStorage.setItem("punishments_row_per_page", rowPerPage);
        setRowPerPage(rowPerPage);
    };
    const columns = [
        {name: "action_type", label: "Type"},
        {name: "reason", label: "Reason"},
        {name: "by", label: "By"},
        {
            name: "time",
            label: "Time",
            options: {
                customBodyRenderLite: (dataIndex) =>
                    moment(punishments[dataIndex].time).format("ddd Do MMM HH:mm:ss"),
            },
        }
    ];

    const options = {
        filter: false,
        rowsPerPage: myRowPerPage,
        selectableRows: "none",
        rowsPerPageOptions: [10, 25, 50, 100, 250, 500, 1000],
        onChangeRowsPerPage: saveRowsPerPage,
    };

    return (
        <MUIDataTable
            title="Punishments"
            data={punishments}
            columns={columns}
            options={options}
        />
    );
}

class PlayerInfo extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            steam_id_64: "",
            created: "0",
            names: [],
            sessions: [],
            sessions_count: 1086,
            total_playtime_seconds: 4495950,
            current_playtime_seconds: 17455,
            received_actions: [],
            penalty_count: {
                TEMPBAN: 0,
                PERMABAN: 0,
                PUNISH: 0,
                KICK: 0
            },
            blacklist: {
                is_blacklisted: false,
                reason: "",
                by: ""
            },
            flags: [],
            watchlist: {},
            steaminfo: {},
            perma: false,
            temp: false,
            vip: false,
            loaded: false
        }
    }

    /**
     * fetch bans that currently affect the steamId64
     * @param steamId64
     */
    fetchPlayerBan(steamId64) {
        get(`get_ban?steam_id_64=${steamId64}`)
            .then((data) => {
                const temp = data.result.find((ban, index) => {
                    return ban.type === "temp";

                })
                const perma = data.result.find((ban, index) => {
                    return ban.type === "perma";
                })
                if (temp !== undefined) {
                    this.setState({temp: true})
                }
                if (perma !== undefined) {
                    this.setState({perma: true})
                }
            })
            .catch(handle_http_errors);
    }

    /**
     * fetch Player data
     * @param steamId64
     */
    fetchPlayer(steamId64) {
        get(`player?steam_id_64=${steamId64}`)
            .then((response) => showResponse(response, "get_user", false))
            .then((data) => {
                if (data.result !== undefined && data.result !== null && Object.keys(data.result).length !== 0) {
                    this.setState({
                        created: data.result.created,
                        names: data.result.names,
                        sessions: data.result.sessions,
                        sessions_count: data.result.sessions_count,
                        total_playtime_seconds: data.result.total_playtime_seconds,
                        current_playtime_seconds: data.result.current_playtime_seconds,
                        received_actions: data.result.received_actions,
                        penalty_count: data.result.penalty_count,
                        blacklist: data.result.blacklist,
                        flags: data.result.flags,
                        watchlist: data.result.watchlist,
                        steaminfo: data.result.steaminfo,
                        loaded: true
                    })
                }
            })
            .catch(handle_http_errors);
    }

    componentDidMount() {
        const {steamId64} = this.props.match.params
        if (steamId64 !== undefined) {
            this.fetchPlayer(steamId64)
            this.fetchPlayerBan(steamId64)
        }
    }

    render() {
        const {classes} = this.props
        return (
            <Grid container className={classes.root}>

                {(this.state.loaded) ?
                    <Grid item sm={12} className={classes.marginTop}>
                        <Grid container>
                            <Grid item sm={2}>
                                <Grid container justify="center" alignContent="center" wrap="wrap"
                                      direction="column" spacing={3}>
                                    <Grid item>
                                        <Avatar style={{height: '150px', width: '150px', fontSize: '5rem'}}
                                                variant="square" className={classes.square}
                                                src={this.state.steaminfo?.profile?.avatarfull}>
                                            {this.state.names[0]?.name[0].toUpperCase()}
                                        </Avatar>
                                    </Grid>
                                    <Grid item>
                                        <Typography variant="h6">Last connection</Typography>
                                        <Typography>{moment(this.state.sessions[0]?.end).format("ddd Do MMM HH:mm:ss")}</Typography>
                                    </Grid>
                                    <Grid item>
                                        <Typography variant="h6">Total play time</Typography>
                                        <Typography>{moment.duration(this.state.total_playtime_seconds, "seconds").humanize()}</Typography>
                                    </Grid>
                                    <Grid item>
                                        <Typography variant="h6">Player penalties</Typography>
                                        <Typography>Perma ban: {this.state.penalty_count.PERMABAN}</Typography>
                                        <Typography>Temp ban: {this.state.penalty_count.TEMPBAN}</Typography>
                                        <Typography>Kick: {this.state.penalty_count.KICK}</Typography>
                                        <Typography>Punish: {this.state.penalty_count.PUNISH}</Typography>
                                    </Grid>
                                </Grid>
                            </Grid>

                            <Grid item sm={9}>
                                <Grid container spacing={3} justify="flex-start" alignItems="flex-start"
                                      alignContent="flex-start">
                                    <Grid item sm={12}>
                                        <Grid container justify="flex-start" alignItems="flex-start"
                                              alignContent="flex-start">
                                            <NamePopOver names={this.state.names}/>
                                        </Grid>
                                    </Grid>
                                    <Grid item sm={4}>
                                        <Grid container sm={12} justify="space-between">
                                            <Grid item>
                                                <Typography color={this.state.vip ? "primary" : ""}
                                                            style={this.state.perma ? "" : {opacity: 0.2}}
                                                            variant="button">VIP
                                                </Typography>
                                            </Grid>
                                            <Grid item>
                                                <Typography color={this.state.perma ? "error" : ""}
                                                            style={this.state.perma ? "" : {opacity: 0.2}}
                                                            variant="button">PERMABAN
                                                </Typography>
                                            </Grid>
                                            <Grid item>
                                                <Typography color={this.state.temp ? "error" : ""}
                                                            style={this.state.perma ? "" : {opacity: 0.2}}
                                                            variant="button">TEMPBAN
                                                </Typography>
                                            </Grid>
                                            <Grid item>
                                                <Typography color={this.state.blacklist?.is_blacklisted ? "error" : ""}
                                                            style={this.state.perma ? "" : {opacity: 0.2}}
                                                            variant="button">BLACKLISTED
                                                </Typography>
                                            </Grid>
                                        </Grid>
                                    </Grid>
                                    <Grid item sm={12}>
                                        <Punishment punishments={this.state.received_actions}/>
                                    </Grid>
                                </Grid>
                            </Grid>
                        </Grid>
                    </Grid>

                    :
                    <div>pending</div>
                }


            </Grid>
        )
    }
}

export default withRouter(PlayerInfo);