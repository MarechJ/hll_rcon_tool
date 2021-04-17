import React from "react";
import { List as iList, Map, fromJS, set } from "immutable";
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
    IconButton
  } from "@material-ui/core";
  import AddIcon from "@material-ui/icons/Add";
  import RemoveIcon from "@material-ui/icons/Remove";
  
  const PlayerItem = ({ score, rank, postProcess, statKey }) => {
    const steamProfile = score.get("steaminfo")
      ? score.get("steaminfo", new Map()).get("profile", new Map())
      : new Map();
    const avatarUrl = steamProfile ? steamProfile.get("avatar", null) : null;
  
    return (
      <React.Fragment>
        <Divider variant="middle" component="li" />
        <ListItem>
          <ListItemAvatar>
            <Avatar src={avatarUrl}></Avatar>
          </ListItemAvatar>
          <ListItemText primary={score.get("player")} secondary={`#${rank}`} />
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
              statKey={statKey} />
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
          postProcessFunc={postProcessFunc} />
      </Paper>
    </React.Fragment>
  );
  

const Scores = ({ classes, scores, durationToHour }) => {
  return (
    <React.Fragment>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/bomb.png"}
          scores={scores}
          title="TOP KILLERS"
          statKey="kills"
          statType="kills"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/invincible.webp"}
          scores={scores}
          title="TOP RATIO"
          statType="kill/death"
          statKey="kill_death_ratio"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/efficiency.png"}
          scores={scores}
          title="TOP PERF."
          statType="kill/minute"
          statKey="kills_per_minute"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/tryhard.png"}
          scores={scores}
          title="TRY HARDERS"
          statType="death/minute"
          statKey="deaths_per_minute"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/stamina.png"}
          scores={scores}
          title="TOP STAMINA"
          statType="deaths"
          statKey="deaths"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/streak_line.png"}
          scores={scores}
          title="TOP KILL STREAK"
          statType="kill streak"
          statKey="kills_streak"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/nevergiveup.png"}
          scores={scores}
          title="I NEVER GIVE UP"
          statType="death streak"
          statKey="deaths_without_kill_streak"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/patience.png"}
          scores={scores}
          title="MOST PATIENT"
          statType="death by teamkill"
          statKey="deaths_by_tk"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/clumsy.png"}
          scores={scores}
          title="YES I'M CLUMSY"
          statType="teamkills"
          statKey="teamkills"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/glasses.png"}
          scores={scores}
          title="I NEED GLASSES"
          statType="teamkills streak"
          statKey="teamkills_streak"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/vote.ico"}
          scores={scores}
          title="I &#10084; VOTING"
          statType="# vote started"
          statKey="nb_vote_started"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/sleep.png"}
          scores={scores}
          title="What is a break?"
          statType="Ingame time"
          statKey="time_seconds"
          reversed
          postProcessFunc={durationToHour} />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/survivor.png"}
          scores={scores}
          title="SURVIVOR"
          statType="Longest life"
          statKey="longest_life_secs"
          reversed />
      </Grid>
      <Grid item xs={12} md={6} lg={3} xl={2}>
        <RankBoard
          classes={classes}
          iconUrl={"icons/early.png"}
          scores={scores}
          title="U'R STILL A MAN"
          statType="Shortest life"
          statKey="longest_life_secs"
          reversed />
      </Grid>
    </React.Fragment>
  );
};


export default Scores;