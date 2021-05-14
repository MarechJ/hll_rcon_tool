import React from "react";
import { List as iList, Map } from "immutable";
import {
  Grid,
  AppBar,
  Link,
  Avatar,
  List,
  ListItem,
  ListItemSecondaryAction,
  ListItemAvatar,
  ListItemText,
  Toolbar,
  Typography,
  Paper,
  Divider,
  IconButton,
  TextField,
} from "@material-ui/core";
import Autocomplete from "@material-ui/lab/Autocomplete";
import { makeStyles } from "@material-ui/core/styles";
import AddIcon from "@material-ui/icons/Add";
import RemoveIcon from "@material-ui/icons/Remove";
import { pure } from "recompose";
import { PlayerStatProfile } from "./PlayerStatProfile";

export const safeGetSteamProfile = (scoreObj) =>
  scoreObj.get("steaminfo")
    ? scoreObj.get("steaminfo", new Map()).get("profile")
      ? scoreObj.get("steaminfo", new Map()).get("profile")
      : new Map()
    : new Map();

const PlayerItem = pure(({ score, rank, postProcess, statKey, onClick }) => {
  const steamProfile = safeGetSteamProfile(score);
  const avatarUrl = steamProfile ? steamProfile.get("avatar", null) : null;

  return (
    <React.Fragment>
      <Divider variant="middle" component="li" />
      <ListItem button onClick={onClick}>
        <ListItemAvatar>
          <Avatar src={avatarUrl}></Avatar>
        </ListItemAvatar>
        <ListItemText
          primary={
            score.get("player") ||
            steamProfile.get(
              "personaname",
              `<missing_profile> ID: ${score.get("player_id")}`
            )
          }
          secondary={`#${rank}`}
        />
        <ListItemSecondaryAction>
          <Typography variant="h6" color="secondary">
            {postProcess(score.get(statKey))}
          </Typography>
        </ListItemSecondaryAction>
      </ListItem>
    </React.Fragment>
  );
});

const TopList = pure(
  ({
    iconUrl,
    scores,
    statType,
    statKey,
    reversed,
    postProcessFunc,
    onPlayerClick,
    playersFilter,
  }) => {
    
    const postProcess = postProcessFunc ? postProcessFunc : (val) => val;
    const defaultNum = playersFilter.size !== 0 ? 100 : 10;
    const [top, setTop] = React.useState(defaultNum);
    const toggle = () => (top ===100 ? setTop(defaultNum) : setTop(100));
    const show = top === 100 ? "Show less" : "Show all";
    const showButton = top === 100 ? <RemoveIcon /> : <AddIcon />;
    const sortedScore = React.useMemo(() => {
      const compareFunc = reversed
      ? (a, b) => (a > b ? -1 : a === b ? 0 : 1)
      : undefined;
      if (playersFilter.size !== 0) {
        return scores.sortBy((s) => s.get(statKey), compareFunc);
      } else {
        return scores.sortBy((s) => s.get(statKey), compareFunc).slice(0, top);
      }
    }, [top, playersFilter, scores, reversed, statKey]);

    return (
      <List>
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
        {sortedScore.map((s, idx) =>
          playersFilter.size === 0 ||
          playersFilter.includes(
            s.get("player") ||
              s.get("steaminfo")?.get("profile")?.get("personaname")
          ) ? (
            <PlayerItem
              key={statKey + idx}
              score={s}
              rank={idx + 1}
              postProcess={postProcess}
              statKey={statKey}
              onClick={() => onPlayerClick(s)}
            />
          ) : (
            ""
          )
        )}
        <ListItem>
          <ListItemAvatar style={{ visibility: "hidden" }}>
            <Avatar>#</Avatar>
          </ListItemAvatar>
          <ListItemText primary={<Link onClick={toggle}>{show}</Link>} />
          <ListItemSecondaryAction>
            <IconButton onClick={toggle} color="secondary">
              {showButton}
            </IconButton>
          </ListItemSecondaryAction>
        </ListItem>
      </List>
    );
  }
);

const RankBoard = pure(
  ({
    classes,
    iconUrl,
    scores,
    title,
    statType,
    statKey,
    reversed,
    postProcessFunc,
    onPlayerClick,
    playersFilter,
  }) => (
    <React.Fragment>
      <AppBar position="relative" style={{ minHeight: "144px" }}>
        <Toolbar style={{ minHeight: "inherit" }}>
          <Typography
            variant="h2"
            align="center"
            className={classes.grow}
            display="block"
          >
            {title}
          </Typography>
        </Toolbar>
      </AppBar>
      <Paper elevation={3}>
        <TopList
          iconUrl={iconUrl}
          scores={scores}
          statType={statType}
          statKey={statKey}
          reversed={reversed}
          postProcessFunc={postProcessFunc}
          onPlayerClick={onPlayerClick}
          playersFilter={playersFilter}
        />
      </Paper>
    </React.Fragment>
  )
);

const useStyles = makeStyles((theme) => ({
  black: {
    backgroundColor: theme.palette.primary.main,
  },
}));

const Scores = pure(({ classes, scores, durationToHour, type }) => {
  const [highlight, setHighlight] = React.useState(null);
  const doHighlight = (playerScore) => {
    setHighlight(playerScore);
    window.scrollTo(0, 0);
  };
  const [playersFilter, setPlayersFilter] = React.useState(new iList());
  const undoHighlight = () => setHighlight(null);
  const styles = useStyles();

  return (
    <React.Fragment>
      {highlight ? (
        <PlayerStatProfile playerScore={highlight} onClose={undoHighlight} />
      ) : (
        ""
      )}
      <Grid item xs={12}>
        <Grid container>
          <Grid item xs={12} className={`${styles.black} ${classes.doublePadding}`}>
            <Paper>
              <Autocomplete
                multiple
                onChange={(e, val) => setPlayersFilter(new iList(val))}
                options={scores
                  .toJS()
                  .map(
                    (v) => v?.player || v.steaminfo?.profile?.personaname || ""
                  )}
                filterSelectedOptions
                renderInput={(params) => (
                  <TextField
                    {...params}
                    variant="outlined"
                    placeholder="Quickly find players by name here (start typing)"
                  />
                )}
              />
            </Paper>
          </Grid>
        </Grid>
      </Grid>
      <Grid item xs={12} className={classes.doublePadding}>
        <Typography variant="caption">
          You can click on a player to see his details
        </Typography>
      </Grid>

      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/bomb.png"}
          scores={scores}
          title="TOP KILLERS"
          statKey="kills"
          statType="kills"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
        />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/invincible.webp"}
          scores={scores}
          title="TOP RATIO"
          statType="kill/death"
          statKey="kill_death_ratio"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
        />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/efficiency.png"}
          scores={scores}
          title="TOP PERF."
          statType="kill/minute"
          statKey="kills_per_minute"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
        />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/tryhard.png"}
          scores={scores}
          title="TRY HARDERS"
          statType="death/minute"
          statKey="deaths_per_minute"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
        />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/stamina.png"}
          scores={scores}
          title="TOP STAMINA"
          statType="deaths"
          statKey="deaths"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
        />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/streak_line.png"}
          scores={scores}
          title="TOP KILL STREAK"
          statType="kill streak"
          statKey="kills_streak"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
        />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/nevergiveup.png"}
          scores={scores}
          title="I NEVER GIVE UP"
          statType="death streak"
          statKey="deaths_without_kill_streak"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
        />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/patience.png"}
          scores={scores}
          title="MOST PATIENT"
          statType="death by teamkill"
          statKey="deaths_by_tk"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
        />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/clumsy.png"}
          scores={scores}
          title="YES I'M CLUMSY"
          statType="teamkills"
          statKey="teamkills"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
        />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/glasses.png"}
          scores={scores}
          title="I NEED GLASSES"
          statType="teamkills streak"
          statKey="teamkills_streak"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
        />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/vote.ico"}
          scores={scores}
          title="I &#10084; VOTING"
          statType="# vote started"
          statKey="nb_vote_started"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
        />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/sleep.png"}
          scores={scores}
          title="What is a break?"
          statType="Ingame time"
          statKey="time_seconds"
          onPlayerClick={doHighlight}
          playersFilter={playersFilter}
          reversed
          postProcessFunc={durationToHour}
        />
      </Grid>
      {type === "live" ? (
        ""
      ) : (
        <React.Fragment>
          <Grid item xs={12} md={6} lg={3} xl={2}>
            <RankBoard
              classes={classes}
              iconUrl={"icons/survivor.png"}
              scores={scores}
              title="SURVIVOR"
              statType="Longest life min."
              statKey="longest_life_secs"
              postProcessFunc={(v) => (v / 60).toFixed(2)}
              onPlayerClick={doHighlight}
              playersFilter={playersFilter}
              reversed
            />
          </Grid>
          <Grid item xs={12} md={6} lg={3} xl={2}>
            <RankBoard
              classes={classes}
              iconUrl={"icons/early.png"}
              scores={scores}
              title="U'R STILL A MAN"
              statType="Shortest life min."
              statKey="shortest_life_secs"
              postProcessFunc={(v) => (v / 60).toFixed(2)}
              onPlayerClick={doHighlight}
              playersFilter={playersFilter}
            />
          </Grid>
        </React.Fragment>
      )}
    </React.Fragment>
  );
});

export default Scores;
