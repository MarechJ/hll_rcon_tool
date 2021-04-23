import {get, handle_http_errors, showResponse} from "../../utils/fetchUtils";
import React from "react";
import "./Player.css"
import {Button, Popover} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import {ExpandMore} from "@material-ui/icons";
import moment from "moment";
import MUIDataTable from "mui-datatables";
import PropTypes from 'prop-types';
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
        <div>
            <Button endIcon={<ExpandMore/>} onClick={handleClick}>
                <div className="name-title">{names[0].name}</div>
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
                    return <Typography className="name">{name.name}</Typography>;
                })}
            </Popover>
        </div>
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
            title={"Punishments"}
            data={punishments}
            columns={columns}
            options={options}
        />
    );
}

class PlayerInfo extends React.Component {
    static propTypes = {
        match: PropTypes.object.isRequired,
        location: PropTypes.object.isRequired,
        history: PropTypes.object.isRequired
    }

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
    #fetchPlayerBan = (steamId64) => {
        get(`get_ban?steam_id_64=${steamId64}`)
            .then((data) => {
                const temp = data.result.find((ban, index) => {
                    if (ban.type === "temp")
                        return true
                })
                const perma = data.result.find((ban, index) => {
                    if (ban.type === "perma")
                        return true
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
    #fetchPlayer = (steamId64) => {
        get(`player?steam_id_64=${steamId64}`)
            .then((response) => showResponse(response, "get_user", false))
            .then((data) => {
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

            })
            .catch(handle_http_errors);
    }

    componentWillReceiveProps(nextProps){
        const { steamId64 } = nextProps.match.params
        if(steamId64 !== undefined){
            this.#fetchPlayer(steamId64)
            this.#fetchPlayerBan(steamId64)
        }
    }

    componentDidMount() {
        const { steamId64 } = this.props.match.params
        if(steamId64 !== undefined){
            this.#fetchPlayer(steamId64)
            this.#fetchPlayerBan(steamId64)
        }
    }

    render() {
        return (
            <div className="player-info">
                <div>
                    {(this.state.loaded) ?
                        <div className="player">
                            <div className="player-col-1">
                                <div className="avatar">
                                    {
                                        (this.state.steaminfo?.profile?.avatarfull !== undefined) ?
                                            <img src={this.state.steaminfo?.profile?.avatarfull} alt="player avatar"/>
                                            :
                                            <span className="letter">{this.state.names[0]?.name[0].toUpperCase()}</span>
                                    }

                                </div>
                                <div>
                                    <h3>Last connection</h3>
                                    <div>{moment(this.state.sessions[0]?.end).format("ddd Do MMM HH:mm:ss")}</div>
                                </div>
                                <div>
                                    <h3>Total play time</h3>
                                    <div>{moment.duration(this.state.total_playtime_seconds, "seconds").humanize()}</div>
                                </div>
                                <div>
                                    <h3>Player penalties</h3>
                                    <div>Perma ban: {this.state.penalty_count.PERMABAN}</div>
                                    <div>Temp ban: {this.state.penalty_count.TEMPBAN}</div>
                                    <div>Kick: {this.state.penalty_count.KICK}</div>
                                    <div>Punish: {this.state.penalty_count.PUNISH}</div>
                                </div>
                            </div>

                            <div className="player-col-2">
                                <div className="names-list">
                                    <NamePopOver names={this.state.names}/>
                                </div>
                                <div className="player-status">
                                    <span className={`vip ${this.state.vip ? "active" : ""}`}>VIP</span>
                                    <span className={`permaban ${this.state.perma ? "active" : ""}`}>PERMABAN</span>
                                    <span className={`tempban ${this.state.temp ? "active" : ""}`}>TEMPBAN</span>
                                    <span
                                        className={`blacklisted ${this.state.blacklist?.is_blacklisted ? "active" : ""}`}>BLACKLISTED</span>
                                </div>
                                <div className="punishments">
                                    <Punishment punishments={this.state.received_actions}/>
                                </div>

                            </div>


                        </div>

                        :
                        <div>pending</div>
                    }

                </div>
                <div className="chat">
                    <div>under construction</div>
                </div>
            </div>
        )
    }
}

export default withRouter(PlayerInfo);