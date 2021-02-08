import { AppBar, Avatar, Grid, List, ListItem, ListItemSecondaryAction, ListItemAvatar, ListItemText, Toolbar, Typography, makeStyles, Paper, Divider } from '@material-ui/core'
import React from 'react'
import { get, handle_http_errors, showResponse } from '../../utils/fetchUtils'
import { List as iList, Map, fromJS } from 'immutable'

const useStyles = makeStyles((theme) => ({

    paper: {
        backgroundColor: theme.palette.background.paper,
    },

}));


const TopList = ({ scores, statType, statKey, reversed }) => {
    const compareFunc = reversed ? (a, b) => a > b ? -1 : a == b ? 0 : 1 : undefined

    return <List>
        <React.Fragment>
            <ListItem>
                <ListItemAvatar style={{ visibility: "hidden" }}>
                    <Avatar></Avatar>
                </ListItemAvatar>
                <ListItemText
                    primary={<Typography variant="h6">name</Typography>}
                />
                <ListItemSecondaryAction>
                    <Typography variant="h6">{statType}</Typography>
                </ListItemSecondaryAction>
            </ListItem>

        </React.Fragment>
        {scores.sortBy((s) => s.get(statKey), compareFunc).slice(0, 20).map((s, idx) => (
            <React.Fragment>
                <Divider variant="middle" component="li" />
                <ListItem>
                    <ListItemAvatar>
                        <Avatar></Avatar>
                    </ListItemAvatar>
                    <ListItemText
                        primary={s.get('player')}
                        secondary={`#${idx+1}`}
                    />
                    <ListItemSecondaryAction>
                        <Typography variant="h6" color="primary">{s.get(statKey)}</Typography>
                    </ListItemSecondaryAction>
                </ListItem>
            </React.Fragment>
        ))}
    </List>
}

const RankBoard = ({ classes, scores, title, statType, statKey, reversed }) => (
    <React.Fragment>
        <AppBar position="relative" >
            <Toolbar>
                <Typography variant="h2" align="center" className={classes.grow} display="block">{title}</Typography>
            </Toolbar>
        </AppBar>
        <Paper elevation={3}>
            <TopList scores={scores} statType={statType} statKey={statKey} reversed={reversed} />
        </Paper>
    </React.Fragment>

)

const LiveScore = ({ classes }) => {
    const styles = useStyles();
    const [scores, setScores] = React.useState(new iList())


    React.useEffect(
        () => (
            get('live_scoreboard').then((res) => showResponse(res, "livescore", false)).then(data => setScores(fromJS(data.result))).catch(handle_http_errors)
        ),
        []
    )

    return <Grid container spacing={2} className={classes.padding}>
        <Grid item xs={12} md={6} lg={3} xs={2}>
            <RankBoard classes={classes} scores={scores} title="TOP KILLERS" statKey="kills" statType="kills" reversed/>
        </Grid>
        <Grid item xs={12} md={6} lg={3} xs={2}>
            <RankBoard classes={classes} scores={scores} title="TOP RATIO" statType="kill/death" statKey="kill_death_ratio" reversed />
        </Grid>
        <Grid item xs={12} md={6} lg={3} xs={2}>
            <RankBoard classes={classes} scores={scores} title="TOP EFFIENCY" statType="kill/minute" statKey="kills_per_minute" reversed />
        </Grid>
        <Grid item xs={12} md={6} lg={3} xs={2}>
            <RankBoard classes={classes} scores={scores} title="TRY HARDERS" statType="death/minute" statKey="deaths_per_minute" reversed />
        </Grid>
        <Grid item xs={12} md={6} lg={3} xs={2}>
            <RankBoard classes={classes} scores={scores} title="TOP PERSITENCY" statType="deaths" statKey="deaths" reversed />
        </Grid>
        <Grid item xs={12} md={6} lg={3} xs={2}>
            <RankBoard classes={classes} scores={scores} title="TOP KILL STREAK" statType="kill streak" statKey="kills_streak" reversed />
        </Grid>
        <Grid item xs={12} md={6} lg={3} xs={2}>
            <RankBoard classes={classes} scores={scores} title="NEVER GIVE UP" statType="death without kill streak" statKey="deaths_without_kill_streak" reversed />
        </Grid>
        <Grid item xs={12} md={6} lg={3} xs={2}>
            <RankBoard classes={classes} scores={scores} title="TOP MOST PATIENT" statType="death by teamkill" statKey="deaths_by_tk" reversed />
        </Grid>
        <Grid item xs={12} md={6} lg={3} xs={2}>
            <RankBoard classes={classes} scores={scores} title="YES I'M CLUMSY" statType="teamkills" statKey="teamkills" reversed />
        </Grid>
        <Grid item xs={12} md={6} lg={3} xs={2}>
            <RankBoard classes={classes} scores={scores} title="I LOVE DEMOCRACY" statType="# vote started" statKey="nb_vote_started" reversed />
        </Grid>
    </Grid>
}

export default LiveScore