import { AppBar, Link, Avatar, Grid, List, ListItem, ListItemSecondaryAction, ListItemAvatar, ListItemText, Toolbar, Typography, makeStyles, Paper, Divider, Card, CardContent, CardMedia, LinearProgress, Select, FormControl, InputLabel, MenuItem, IconButton, Chip } from '@material-ui/core'
import React from 'react'
import { get, handle_http_errors, showResponse } from '../../utils/fetchUtils'
import { List as iList, Map, fromJS, set } from 'immutable'
import moment from 'moment'
import AddIcon from '@material-ui/icons/Add';
import RemoveIcon from '@material-ui/icons/Remove';


const useStyles = makeStyles((theme) => ({

    paper: {
        backgroundColor: theme.palette.background.paper,
    },
    transparentPaper: {
        backgroundColor: theme.palette.background.paper,
        opacity: "0.6",
        borderRadius: "0px"
    },
    root: {
        display: 'flex',
    },
    details: {
        display: 'flex',
        flexDirection: 'column',
    },
    content: {
        flex: '1 0 auto',
    },
    cover: {
        width: 200,
    },
    controls: {
        display: 'flex',
        alignItems: 'center',
        paddingLeft: theme.spacing(1),
        paddingBottom: theme.spacing(1),
    },
    playIcon: {
        height: 38,
        width: 38,
    },
}));

const map_to_pict = {
    'carentan': 'maps/carentan.webp',
    'foy': 'maps/foy.webp',
    'hill400': 'maps/hill400.webp',
    'hurtgenforest': 'maps/hurtgen.webp',
    'omahabeach': 'maps/omaha.webp',
    'purpleheartlane': 'maps/omaha.webp',
    'stmariedumont': 'maps/smdm.webp',
    'stmereeglise': 'maps/sme.webp',
    'utahbeach': 'maps/utah.webp'
}

const PlayerItem = ({ score, rank, postProcess, statKey }) => {
    const steamProfile = score.get('steaminfo') ? score.get("steaminfo", new Map()).get("profile", new Map()) : new Map()
    const avatarUrl = steamProfile ? steamProfile.get("avatar", null) : null

    return <React.Fragment>
        <Divider variant="middle" component="li" />
        <ListItem>
            <ListItemAvatar>
                <Avatar src={avatarUrl}></Avatar>
            </ListItemAvatar>
            <ListItemText
                primary={score.get('player')}
                secondary={`#${rank}`}
            />
            <ListItemSecondaryAction>
                <Typography variant="h6" color="secondary">{postProcess(score.get(statKey))}</Typography>
            </ListItemSecondaryAction>
        </ListItem>
    </React.Fragment>
}

const TopList = ({ iconUrl, scores, statType, statKey, reversed, postProcessFunc }) => {
    const compareFunc = reversed ? (a, b) => a > b ? -1 : a == b ? 0 : 1 : undefined
    const postProcess = postProcessFunc ? postProcessFunc : val => val
    const defaultNum = 10
    const [top, setTop] = React.useState(defaultNum)
    const toggle = () => top == 100 ? setTop(defaultNum) : setTop(100)
    const show = top == 100 ? "Show less" : "Show all"
    const showButton = top == 100 ? <RemoveIcon/> : <AddIcon />

    return <List>
        <React.Fragment>
            <ListItem>
                <ListItemAvatar style={{ visibility: "visible" }}>
                    <Avatar src={iconUrl}>#</Avatar>
                </ListItemAvatar>
                <ListItemText
                    primary={<Typography variant="h6">name</Typography>}
                />
                <ListItemSecondaryAction>
                    <Typography variant="h6">{statType}</Typography>
                </ListItemSecondaryAction>
            </ListItem>

        </React.Fragment>
        {scores.sortBy((s) => s.get(statKey), compareFunc).slice(0, top).map((s, idx) => (
            <PlayerItem score={s} rank={idx + 1} postProcess={postProcess} statKey={statKey} />
        ))}
        <ListItem>
                <ListItemAvatar style={{ visibility: "hidden" }}>
                    <Avatar>#</Avatar>
                </ListItemAvatar>
                <ListItemText
                    primary={<Link onClick={toggle}>{show}</Link>}
                />
                <ListItemSecondaryAction>
                    <IconButton onClick={toggle} color="secondary">
                        {showButton}
                    </IconButton>
                </ListItemSecondaryAction>
                </ListItem>
    </List>
}

const RankBoard = ({ classes, iconUrl, scores, title, statType, statKey, reversed, postProcessFunc }) => (
    <React.Fragment>
        <AppBar position="relative" style={{ minHeight: "144px" }} >
            <Toolbar style={{ minHeight: "inherit" }}>
                <Typography variant="h2" align="center" className={classes.grow} display="block">{title}</Typography>
            </Toolbar>
        </AppBar>
        <Paper elevation={3}>
            <TopList iconUrl={iconUrl} scores={scores} statType={statType} statKey={statKey} reversed={reversed} postProcessFunc={postProcessFunc} />
        </Paper>
    </React.Fragment>

)


const LiveScore = ({ classes }) => {
    const styles = useStyles();
    const [stats, setStats] = React.useState(new iList())
    const [serverState, setServerState] = React.useState(new Map())
    const [isLoading, setIsLoading] = React.useState(true)
    const [isPaused, setPaused] = React.useState(false)
    const [refreshIntervalSec, setRefreshIntervalSec] = React.useState(10)
    const durationToHour = (val) => new Date(val * 1000).toISOString().substr(11, 5) 
    const scores = stats.get("stats", new iList())
    const lastRefresh = stats.get("snapshot_timestamp") ? moment.unix(stats.get("snapshot_timestamp")).format() : "N/A"

    const getData = () => {
        setIsLoading(true)
        console.log("Loading data")
        get('public_info').then((res) => showResponse(res, "public_info", false)).then(data => setServerState(fromJS(data.result))).then(() => setIsLoading(false)).catch(handle_http_errors)
        get('live_scoreboard').then((res) => showResponse(res, "livescore", false)).then(data => setStats(fromJS(data.result))).catch(handle_http_errors)
    }

    React.useEffect(
        () => {
            if (!isPaused) {
                const interval = setInterval(getData, refreshIntervalSec * 1000);
                return () => clearInterval(interval);
            }
            
        }, [isPaused]
    )

    document.title = serverState.get('name', "HLL Stats")
    let started = serverState.get("current_map", new Map()).get("start")
    started = started ? new Date(Date.now() - new Date(started * 1000)).toISOString().substr(11, 8) : "N/A"

    return <React.Fragment><Grid container spacing={2}
        justify="center"
        className={classes.padding}>
        <Grid xs={12} md={10} lg={10} xl={8} className={classes.doublePadding}>
            <AppBar position="relative" style={{ minHeight: "144px" }} >
                <Toolbar className={classes.doublePadding} >
                    <Grid container justify="flex-start" alignItems="flex-start" alignContent="flex=start" spacing={1}>
                        <Grid item xs={3} md={2} lg={2} alignContent="center" alignItems="center" justify="center" style={{
                            flex: "grow",
                            maxWidth: "220px",
                            backgroundRepeat: "no-repeat",
                            backgroundSize: "auto 150px",
                            backgroundImage: `url(${map_to_pict[serverState.get("current_map", new Map()).get("just_name", "foy")]})`, minHeight: "150px"
                        }} >
                            <Paper elevation={0} className={styles.transparentPaper}><Typography variant="caption">Current map</Typography></Paper>
                            <Paper elevation={0} className={styles.transparentPaper}><Typography variant="h6">{serverState.get("current_map", new Map()).get("human_name", "N/A")}</Typography></Paper>
                            <Paper elevation={0} className={styles.transparentPaper}><Typography variant="caption">Elapsed: {started}</Typography></Paper>
                            <Paper elevation={0} className={styles.transparentPaper}><Typography variant="caption">Players: {serverState.get("nb_players")}</Typography></Paper>
                        </Grid>
                        <Grid item xs={9}>
                            <Grid container spacing={1}>
                                <Grid item xs={12}> <Typography variant="h4" display="inline" color="secondary">LIVE STATS</Typography></Grid>
                                <Grid item xs={12}><Typography variant="h4">{serverState.get('name')}</Typography></Grid>
                                <Grid item xs={12}>
                                    <Typography variant="caption">Only ingame players are shown. Stats reset on disconnection, not per game. Real deaths only (excludes redeploys / revives)</Typography>
                                </Grid>
                                <Grid item xs={12}>
                                    <Typography variant="caption">Last update: {lastRefresh} - Auto-refresh {refreshIntervalSec} sec: <Link onClick={() => setPaused(!isPaused)} color="secondary">{isPaused ? "unpause" : "pause"}</Link></Typography>
                                </Grid>
                            </Grid>
                        </Grid>
                        <Grid item xs={12}>
                            <LinearProgress style={{ visibility: isLoading ? "visible" : "hidden" }} className={classes.grow} color="secondary" />
                        </Grid>
                    </Grid>

                </Toolbar>
            </AppBar>
        </Grid>
    </Grid>
        <Grid container spacing={2}
            justify="center"
            className={classes.padding}>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/bomb.png"} scores={scores} title="TOP KILLERS" statKey="kills" statType="kills" reversed />
            </Grid>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/invincible.webp"} scores={scores} title="TOP RATIO" statType="kill/death" statKey="kill_death_ratio" reversed />
            </Grid>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/efficiency.png"} scores={scores} title="TOP PERF." statType="kill/minute" statKey="kills_per_minute" reversed />
            </Grid>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/tryhard.png"} scores={scores} title="TRY HARDERS" statType="death/minute" statKey="deaths_per_minute" reversed />
            </Grid>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/stamina.png"} scores={scores} title="TOP STAMINA" statType="deaths" statKey="deaths" reversed />
            </Grid>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/streak_line.png"} scores={scores} title="TOP KILL STREAK" statType="kill streak" statKey="kills_streak" reversed />
            </Grid>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/nevergiveup.png"} scores={scores} title="I NEVER GIVE UP" statType="death streak" statKey="deaths_without_kill_streak" reversed />
            </Grid>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/patience.png"} scores={scores} title="MOST PATIENT" statType="death by teamkill" statKey="deaths_by_tk" reversed />
            </Grid>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/clumsy.png"} scores={scores} title="YES I'M CLUMSY" statType="teamkills" statKey="teamkills" reversed />
            </Grid>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/glasses.png"} scores={scores} title="I NEED GLASSES" statType="teamkills streak" statKey="teamkills_streak" reversed />
            </Grid>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/vote.ico"} scores={scores} title="I &#10084; VOTING" statType="# vote started" statKey="nb_vote_started" reversed />
            </Grid>
            <Grid item xs={12} md={6} lg={3} xl={2}>
                <RankBoard classes={classes} iconUrl={"icons/sleep.png"} scores={scores} title="What is a break?" statType="Ingame time" statKey="time_seconds" reversed postProcessFunc={durationToHour} />
            </Grid>
        </Grid >
    </React.Fragment>
}

export default LiveScore