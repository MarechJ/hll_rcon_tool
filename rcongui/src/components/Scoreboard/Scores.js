import React from "react";
import { List as iList, Map, fromJS, set, Set } from "immutable";
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
  Collapse,
} from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import AddIcon from "@material-ui/icons/Add";
import RemoveIcon from "@material-ui/icons/Remove";
import ExpandLess from "@material-ui/icons/ExpandLess";
import ExpandMore from "@material-ui/icons/ExpandMore";
import CancelIcon from '@material-ui/icons/Cancel';

const safeGetSteamProfile = (scoreObj) =>
  scoreObj.get("steaminfo")
    ? scoreObj.get("steaminfo", new Map()).get("profile")
      ? scoreObj.get("steaminfo", new Map()).get("profile")
      : new Map()
    : new Map();

const PlayerItem = ({ score, rank, postProcess, statKey, onClick }) => {
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
};
const TopList = ({
  iconUrl,
  scores,
  statType,
  statKey,
  reversed,
  postProcessFunc,
  onPlayerClick
}) => {
  const compareFunc = reversed
    ? (a, b) => (a > b ? -1 : a == b ? 0 : 1)
    : undefined;
  const postProcess = postProcessFunc ? postProcessFunc : (val) => val;
  const defaultNum = 10;
  const [top, setTop] = React.useState(defaultNum);
  const toggle = () => (top == 100 ? setTop(defaultNum) : setTop(100));
  const show = top == 100 ? "Show less" : "Show all";
  const showButton = top == 100 ? <RemoveIcon /> : <AddIcon />;

  return (
    <List>
      <React.Fragment>
        <ListItem>
          <ListItemAvatar style={{ visibility: "visible" }}>
            <Avatar src={iconUrl}>#</Avatar>
          </ListItemAvatar>
          <ListItemText primary={<Typography variant="h6">name</Typography>} />
          <ListItemSecondaryAction>
            <Typography variant="h6">{statType}</Typography>
          </ListItemSecondaryAction>
        </ListItem>
      </React.Fragment>
      {scores
        .sortBy((s) => s.get(statKey), compareFunc)
        .slice(0, top)
        .map((s, idx) => (
          <PlayerItem
            score={s}
            rank={idx + 1}
            postProcess={postProcess}
            statKey={statKey}
            onClick={() => onPlayerClick(s)}
          />
        ))}
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
};

const RankBoard = ({
  classes,
  iconUrl,
  scores,
  title,
  statType,
  statKey,
  reversed,
  postProcessFunc,
  onPlayerClick,
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
      />
    </Paper>
  </React.Fragment>
);

const useStyles = makeStyles((theme) => ({
  nested: {
    paddingLeft: theme.spacing(4),
  },
}));

const SubList = ({ playerScore, dataMapKey, title, openDefault }) => {
  const data = dataMapKey
    ? playerScore.get(dataMapKey) || new Map()
    : playerScore;
  const styles = useStyles();
  const [open, setOpen] = React.useState(openDefault);

  return (
    <React.Fragment>
      <ListItem button onClick={() => setOpen(!open)}>
        <ListItemText primary={<Typography variant="h5">{title}</Typography>} />
        <ListItemSecondaryAction>
          <IconButton onClick={() => setOpen(!open)}>{open ? <ExpandLess /> : <ExpandMore />}</IconButton>
          </ListItemSecondaryAction>
      </ListItem>
      <Collapse in={open} timeout="auto" unmountOnExit>
        <List component="div" disablePadding dense>
          {data
            .sort()
            .reverse()
            .entrySeq()
            .map(([key, value]) => (
              <ListItem className={styles.nested}>
                <ListItemText primary={key} />
                <ListItemSecondaryAction>
                  <Typography variant="h6" color="secondary">
                    {value}
                  </Typography>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
        </List>
      </Collapse>
    </React.Fragment>
  );
};

const PlayerStatProfile = ({ playerScore, onClose }) => {
  const steamProfile = safeGetSteamProfile(playerScore);
  const excludedKeys = new Set([
    "player_id",
    "id",
    "steaminfo",
    "map_id",
    "most_killed",
    "weapons",
    "death_by",
  ]);

  return (
    <Grid item xs={12}>
      <Grid container justify="center">
        <Grid item xs={12} md={6} lg={4} xl={2}>
          <Paper>
            <List>
              <ListItem divider>
                <ListItemAvatar>
                  <Avatar src={steamProfile.get("avatar")}></Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Typography variant="h4">
                     <Link color="inherit" href={steamProfile.get("profileurl")} target="_blank">{playerScore.get("player") ||
                        steamProfile.get("personaname")}</Link> 
                    </Typography>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton onClick={onClose}><CancelIcon/></IconButton>
                </ListItemSecondaryAction>
              </ListItem>
              <SubList
                playerScore={playerScore}
                dataMapKey="weapons"
                title="Kills by weapons"
                openDefault
                
              />
              <SubList
                playerScore={playerScore}
                dataMapKey="most_killed"
                title="Kills by player"
              />
              <SubList
                playerScore={playerScore}
                dataMapKey="death_by"
                title="Deaths by player"
              />
              <SubList
                playerScore={playerScore.filterNot((v, k) =>
                  excludedKeys.has(k)
                )}
                title="Raw stats"
              />
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Grid>
  );
};

const Scores = ({ classes, scores, durationToHour }) => {
  const [highlight, setHighlight] = React.useState(null)
  const doHighlight = (playerScore) => {setHighlight(playerScore); window.scrollTo(0, 0);} 
  const undoHighlight = () => setHighlight(null)
  return (
    <React.Fragment>
      {highlight ? <PlayerStatProfile playerScore={highlight} onClose={undoHighlight} /> : ""}
      <Grid item xs={12}>
        <Typography variant="caption">Click on a plyer to see details</Typography>
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
          reversed
          postProcessFunc={durationToHour}
        />
      </Grid>
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
        />
      </Grid>
    </React.Fragment>
  );
};

export default Scores;
