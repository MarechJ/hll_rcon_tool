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
import MUIDataTable from "mui-datatables";
import { Button } from "@material-ui/core";
import { fromJS } from "immutable";
import { toPairs, sortBy } from "lodash";

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
    const defaultNum = playersFilter.size !== 0 ? 9999 : 10;
    const [top, setTop] = React.useState(defaultNum);
    const toggle = () => (top === 9999 ? setTop(defaultNum) : setTop(9999));
    const show = top === 9999 ? "Show less" : "Show all";
    const showButton = top === 9999 ? <RemoveIcon /> : <AddIcon />;
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

const RawScores = pure(({ classes, scores }) => {
  const lastState = window.localStorage.getItem("rawStats");
  const [show, setShow] = React.useState(
    lastState !== null
      ? parseInt(lastState)
      : process.env.REACT_APP_PUBLIC_BUILD
      ? 0
      : 1
  );
  const [rowsPerPage, setRowsPerPage] = React.useState(50);
  const [columns, setColumns] = React.useState([
    { name: "steaminfo.profile.steamid", label: "Steam ID", options: {display: false}, },
    { name: "player", label: "Name" },
    { name: "kills", label: "Kills" },
    { name: "deaths", label: "Deaths" },
    { name: "kill_death_ratio", label: "K/D" },
    { name: "kills_streak", label: "Max kill streak" },
    { name: "kills_per_minute", label: "Kill(s) / minute" },
    { name: "deaths_per_minute", label: "Death(s) / minute" },
    {
      name: "deaths_without_kill_streak",
      label: "Max death streak",
    },
    { name: "teamkills", label: "Max TK streak" },
    { name: "deaths_by_tk", label: "Death by TK" },
    { name: "deaths_by_tk_streak", label: "Death by TK Streak" },
    {
      name: "longest_life_secs",
      label: "(aprox.) Longest life min.",
      options: {
        customBodyRender: (value, tableMeta, updateValue) =>
          Math.round(parseInt(value) / 60).toFixed(2),
      },
    },
    {
      name: "shortest_life_secs",
      label: "(aprox.) Shortest life secs.",
      options: {
        customBodyRender: (value, tableMeta, updateValue) =>
          Math.round(parseInt(value) / 60).toFixed(2),
      },
    },
    {
      name: "death_by",
      label: "Nemesis",
      options: {
        customBodyRender: (value, tableMeta, updateValue) => {
          const pairs = toPairs(value);
          return sortBy(pairs, (v) => -v[1]).map(
            (v) => `${v[0]}: ${v[1]}`
          )[0];
        },
      },
    },
    {
      name: "most_killed",
      label: "Victim",
      options: {
        customBodyRender: (value, tableMeta, updateValue) => {
          const pairs = toPairs(value);
          return sortBy(pairs, (v) => -v[1]).map(
            (v) => `${v[0]}: ${v[1]}`
          )[0];
        },
      },
    },
    { name: "combat", label: "Combat Effectiveness", options: {display: false} },
    { name: "support", label: "Support Points", options: {display: false} },
    { name: "defense", label: "Defensive Points", options: {display: false} },
    { name: "offense", label: "Offensive Points", options: {display: false} },
    {
      name: "weapons",
      label: "Weapons",
      options: {
        customBodyRender: commaSeperatedListRenderer,
      },
    },
    {
      name: "death_by_weapons",
      label: "Death by Weapons",
      options: {
        customBodyRender: commaSeperatedListRenderer,
      },
    },
  ]);
  return (
    <Grid container spacing={2} className={classes.padding}>
      <Grid item xs={12}>
        <Button
          onClick={() => {
            window.localStorage.setItem("rawStats", show === 0 ? 1 : 0);
            setShow(show === 0 ? 1 : 0);
          }}
          variant="outlined"
        >
          {show ? "hide" : "show"} raw stats
        </Button>
      </Grid>{" "}
      {show ? (
        <Grid item xs={12}>
          <MUIDataTable
            options={{
              filter: false,
              rowsPerPage: rowsPerPage,
              enableNestedDataAccess: '.',
              selectableRows: "none",
              rowsPerPageOptions: [10, 25, 50, 100, 250, 500, 1000],
              onChangeRowsPerPage: (v) => setRowsPerPage(v),
              onViewColumnsChange: (c, a) => {
                setColumns((cc) => {
                  const newColumns = [...cc];
                  const changedColumn = newColumns.find((column) => column.name === c);
                  if (!changedColumn.options) {
                    changedColumn.options = {display: a === 'add'};
                  } else {
                    changedColumn.options.display = a === 'add';
                  }
                  return newColumns;
                });
              },
              onDownload: (buildHead, buildBody, columns, data) => {
                // Convert any column values that are objects to JSON so they display in the csv as data instead of [object Object]
                const expandedData = data.map((row) => {
                  return {
                    index: row.index,
                    data: row.data.map((colValue) =>
                      typeof colValue === "object"
                        ? JSON.stringify(colValue)
                        : colValue
                    ),
                  };
                });
                return buildHead(columns) + buildBody(expandedData);
              },
            }}
            data={scores ? scores.toJS() : []}
            columns={columns}
          />
        </Grid>
      ) : (
        ""
      )}
    </Grid>
  );
});

function commaSeperatedListRenderer(value) {
  const pairs = toPairs(value);
  return sortBy(pairs, (v) => -v[1])
    .map((v) => `${v[0]}: ${v[1]}`)
    .join(", ");
}

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
      {scores && scores.size ? (
        <React.Fragment>
          {process.env.REACT_APP_PUBLIC_BUILD ? (
            ""
          ) : (
            <Grid item xs={12}>
              <RawScores scores={scores} classes={classes} />{" "}
            </Grid>
          )}

          <Grid item xs={12}>
            <Grid container>
              <Grid
                item
                xs={12}
                className={`${styles.black} ${classes.doublePadding}`}
              >
                <Paper>
                  <Autocomplete
                    multiple
                    onChange={(e, val) => setPlayersFilter(new iList(val))}
                    options={scores
                      .toJS()
                      .map(
                        (v) =>
                          v?.player || v.steaminfo?.profile?.personaname || ""
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
              title="I ❤ VOTING"
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
            {process.env.REACT_APP_PUBLIC_BUILD ? (
              <Grid item xs={12}>
                <RawScores scores={scores} classes={classes} />{" "}
              </Grid>
            ) : (
              ""
            )}
          </React.Fragment>
        </React.Fragment>
      ) : (
        <Grid item xs={12}>
          <Typography variant="h4">No stats available yet</Typography>
        </Grid>
      )}
    </React.Fragment>
  );
});

export default Scores;
