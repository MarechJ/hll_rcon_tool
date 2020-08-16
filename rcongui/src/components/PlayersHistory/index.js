/* eslint-disable no-use-before-define */
import React from "react";
import useAutocomplete from "@material-ui/lab/useAutocomplete";
import { postData, showResponse, sendAction } from "../../utils/fetchUtils";
import { toast } from "react-toastify";
import { join, reduce } from "lodash";
import Pagination from "@material-ui/lab/Pagination";
import {
  Grid,
  Button,
  TextField,
  LinearProgress,
  Chip,
} from "@material-ui/core";
import { ReasonDialog } from "../PlayerView/playerActions";
import { omitBy } from "lodash/object";
import SearchBar from "./searchBar";
import { Map, List } from "immutable";
import FlagIcon from "@material-ui/icons/Flag";
import "emoji-mart/css/emoji-mart.css";
import { Picker } from "emoji-mart";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import { getEmojiFlag } from "../../utils/emoji";
import PlayerItem from "./playerItem";

const PlayerSummary = ({ player, flag }) => (
  <React.Fragment>
    <p>Add flag: {flag ? getEmojiFlag(flag) : <small>Please choose</small>}</p>
    <p>
      To:{" "}
      {player.names
        ? player.names.map((n) => <Chip label={n} />)
        : "No name recorded"}
    </p>
    <p>Steamd id: {player.steam_id_64}</p>
  </React.Fragment>
);

class FlagDialog extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      flag: null,
      comment: "",
    };
  }

  render() {
    const { open, handleClose, handleConfirm, SummaryRenderer } = this.props;
    const { flag, comment } = this.state;

    return (
      <Dialog open={open} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">
          <SummaryRenderer player={open} flag={flag} />
        </DialogTitle>
        <DialogContent>
          <Grid
            container
            alignContent="center"
            alignItems="center"
            justify="center"
            spacing={2}
          >
            <Grid item xs={12}>
              <TextField
                label="Comment"
                value={comment}
                onChange={(e) => this.setState({ comment: e.target.value })}
              />
            </Grid>
          </Grid>
          <Grid
            container
            alignContent="center"
            alignItems="center"
            justify="center"
            spacing={2}
          >
            <Grid item xs={12}>
              <Picker
                onSelect={(emoji) => this.setState({ flag: emoji.native })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              this.setState({ flag: "" });
              handleClose();
            }}
            color="primary"
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              handleConfirm(open, flag, comment);
              this.setState({ flag: "", comment: "" });
            }}
            color="primary"
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    );
  }
}

const show_names = (names) => join(names, " · ");

const FlagButton = ({ classes, onflag }) => (
  <Button variant="outlined" onClick={onflag}>
    <FlagIcon />
  </Button>
);

const MyPagination = ({ classes, pageSize, total, page, setPage }) => (
  <Pagination
    count={Math.ceil(total / pageSize)}
    page={page}
    onChange={(e, val) => setPage(val)}
    variant="outlined"
    color="default"
    showFirstButton
    showLastButton
    className={classes.pagination}
  />
);

const FilterPlayer = ({
  classes,
  constPlayersHistory,
  pageSize,
  total,
  page,
  setPage,
  onUnBlacklist,
  onBlacklist,
  constNamesIndex,
  onAddFlag,
  onDeleteFlag,
  onAddVip,
  onDeleteVip,
  vips,
}) => {
  const playersHistory = constPlayersHistory.toJS();
  const namesIndex = constNamesIndex.toJS();
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
    getOptionLabel: (option) => (option.names ? option.names : option),
  });

  const [doFlag, setDoFlag] = React.useState(false);
  const [doConfirmPlayer, setDoConfirmPlayer] = React.useState(false);
  const playerList = groupedOptions.length > 0 ? groupedOptions : namesIndex;

  return (
    <div>
      <Grid
        container
        {...getRootProps()}
        alignContent="space-between"
        alignItems="flex-end"
        spacing={2}
      >
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            inputProps={{ ...getInputProps() }}
            label="Filter current selection"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <MyPagination
            classes={classes}
            pageSize={pageSize}
            page={page}
            setPage={setPage}
            total={total}
          />
        </Grid>
      </Grid>
      <Grid container spacing={2}>
          
        {playerList.map((nameIndex) => {
          const player = playersHistory[nameIndex.idx];

          return (
            <Grid
              key={player.steam_id_64}
              item
              xs={12}
              sm={6}
              md={4}
              lg={3}
              xl={2}
            >
              <PlayerItem
                key={player.steam_id_64}
                classes={classes}
                names={show_names(player.names)}
                steamId64={player.steam_id_64}
                firstSeen={player.first_seen_timestamp_ms}
                lastSeen={player.last_seen_timestamp_ms}
                punish={player.penalty_count.PUNISH}
                kick={player.penalty_count.KICK}
                tempban={player.penalty_count.TEMPBAN}
                permaban={player.penalty_count.PERMABAN}
                compact={false}
                blacklisted={player.blacklisted}
                flags={List(player.flags.map((v) => Map(v)))}
                onflag={() => setDoFlag(player)}
                onBlacklist={() =>
                  setDoConfirmPlayer({
                    player: player.steam_id_64,
                    actionType: "blacklist",
                  })
                }
                onUnBlacklist={() => onUnBlacklist(player.steam_id_64)}
                onDeleteFlag={onDeleteFlag}
                onAddVip={() => onAddVip(player.names[0], player.steam_id_64)}
                onDeleteVip={() => onDeleteVip(player.steam_id_64)}
                isVip={vips[player.steam_id_64]}
              />
            </Grid>
          );
        })}
        <Grid item xs={12}>
          <MyPagination
            classes={classes}
            pageSize={pageSize}
            page={page}
            setPage={setPage}
            total={total}
          />
        </Grid>
      </Grid>
      <ReasonDialog
        open={doConfirmPlayer}
        handleClose={() => setDoConfirmPlayer(false)}
        handleConfirm={(actionType, steamId64, reason) => {
          onBlacklist(steamId64, reason);
          setDoConfirmPlayer(false);
        }}
      />
      <FlagDialog
        open={doFlag}
        handleClose={() => setDoFlag(false)}
        handleConfirm={(playerObj, theFlag, theComment) => {
          onAddFlag(playerObj, theFlag, theComment);
          setDoFlag(false);
        }}
        SummaryRenderer={PlayerSummary}
      />
    </div>
  );
};

class PlayersHistory extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      playersHistory: List(),
      namesIndex: List(),
      total: 0,
      pageSize: 50,
      page: 1,
      byName: "",
      bySteamId: "",
      blacklistedOnly: false,
      lastSeenFrom: null,
      lastSeenUntil: null,
      isLoading: true,
      vips: {},
    };

    this.getPlayerHistory = this.getPlayerHistory.bind(this);
    this.blacklistPlayer = this.blacklistPlayer.bind(this);
    this.unblacklistPlayer = this.unblacklistPlayer.bind(this);
    this.addFlagToPlayer = this.addFlagToPlayer.bind(this);
    this.deleteFlag = this.deleteFlag.bind(this);
    this.loadVips = this.loadVips.bind(this);
    this.onAddVip = this.onAddVip.bind(this);
    this.onDeleteVip = this.onDeleteVip.bind(this);
  }

  onAddVip(name, steamID64) {
    return sendAction("do_add_vip", {
      steam_id_64: steamID64,
      name: name,
    }).then(this.loadVips);
  }

  onDeleteVip(steamID64) {
    return sendAction("do_remove_vip", { steam_id_64: steamID64 }).then(
      this.loadVips
    );
  }

  _loadToState(command, showSuccess, stateSetter) {
    return fetch(`${process.env.REACT_APP_API_URL}${command}`)
      .then((res) => showResponse(res, command, showSuccess))
      .then(stateSetter)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  loadVips() {
    return this._loadToState("get_vip_ids", false, (data) =>
      this.setState({
        vips: reduce(
          data.result,
          (acc, val) => {
            acc[val.steam_id_64] = true;
            return acc
          },
          {}
        ),
      })
    );
  }

  getPlayerHistory() {
    const {
      pageSize,
      page,
      byName,
      bySteamId,
      blacklistedOnly,
      lastSeenFrom,
      lastSeenUntil,
    } = this.state;
    const params = omitBy(
      {
        page_size: pageSize,
        page: page,
        player_name: byName,
        steam_id_64: bySteamId,
        blacklisted: blacklistedOnly,
        last_seen_from: lastSeenFrom,
        last_seen_until: lastSeenUntil,
      },
      (v) => !v
    );

    this.setState({ isLoading: true });
    return postData(`${process.env.REACT_APP_API_URL}players_history`, params)
      .then((response) => showResponse(response, "player_history"))
      .then((data) => {
        this.setState({ isLoading: false });
        if (data.failed) {
          return;
        }
        this.setState({
          playersHistory: List(data.result.players),
          namesIndex: List(
            data.result.players.map((el, idx) => ({
              names: join(el.names, ","),
              idx: idx,
            }))
          ),
          total: data.result.total,
          pageSize: data.result.page_size,
          page: data.result.page,
        });
      })
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  _reloadOnSuccess = (data) => {
    if (data.failed) {
      return;
    }
    this.getPlayerHistory();
    this.loadVips();
  };

  addFlagToPlayer(playerObj, flag, comment = null) {
    return postData(`${process.env.REACT_APP_API_URL}flag_player`, {
      steam_id_64: playerObj.steam_id_64,
      flag: flag,
      comment: comment,
    })
      .then((response) => showResponse(response, "flag_player"))
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  deleteFlag(flag_id) {
    return postData(`${process.env.REACT_APP_API_URL}unflag_player`, {
      flag_id: flag_id,
    })
      .then((response) => showResponse(response, "unflag_player"))
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  blacklistPlayer(steamId64, reason) {
    postData(`${process.env.REACT_APP_API_URL}blacklist_player`, {
      steam_id_64: steamId64,
      reason: reason,
    })
      .then((response) =>
        showResponse(
          response,
          `PlayerID ${steamId64} blacklist for ${reason}`,
          true
        )
      )
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  unblacklistPlayer(steamId64) {
    postData(`${process.env.REACT_APP_API_URL}unblacklist_player`, {
      steam_id_64: steamId64,
    })
      .then((response) =>
        showResponse(
          response,
          `PlayerID ${steamId64} removed from blacklist`,
          true
        )
      )
      .then(this._reloadOnSuccess)
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  componentDidMount() {
    this.getPlayerHistory();
    this.loadVips();
  }

  render() {
    const { classes } = this.props;
    const {
      playersHistory,
      pageSize,
      page,
      total,
      byName,
      bySteamId,
      blacklistedOnly,
      lastSeenFrom,
      lastSeenUntil,
      isLoading,
      namesIndex,
    } = this.state;

    // There's a bug in the autocomplete code, if there's a boolean in the object it makes it match against
    // "false" or "true" so essentially, everything matches to "F" or "T"
    // That's why we remap the list

    // Perfomance is crappy. It's less crappy after switcing to immutables but still...
    // It should be refactored so that the search bar does not trigger useless renderings
    return (
      <Grid container className={classes.padding}>
        <Grid item xs={12}>
          <SearchBar
            pageSize={pageSize}
            setPageSize={(v) => this.setState({ pageSize: v })}
            lastSeenFrom={lastSeenFrom}
            setLastSeenFrom={(v) => this.setState({ lastSeenFrom: v })}
            lastSeenUntil={lastSeenUntil}
            setLastSeenUntil={(v) => this.setState({ lastSeenUntil: v })}
            name={byName}
            setName={(v) => this.setState({ byName: v })}
            steamId={bySteamId}
            setSteamId={(v) => this.setState({ bySteamId: v })}
            blacklistedOnly={blacklistedOnly}
            setBlacklistedOnly={(v) => this.setState({ blacklistedOnly: v })}
            onSearch={this.getPlayerHistory}
          />
        </Grid>
        <Grid item xs={12}>
          {isLoading ? (
            <Grid item xs={12} className={classes.doublePadding}>
              <LinearProgress color="secondary" />
            </Grid>
          ) : (
            <FilterPlayer
              classes={classes}
              constPlayersHistory={playersHistory}
              constNamesIndex={namesIndex}
              pageSize={pageSize}
              total={total}
              page={page}
              setPage={(page) =>
                this.setState({ page: page }, this.getPlayerHistory)
              }
              onBlacklist={this.blacklistPlayer}
              onUnBlacklist={this.unblacklistPlayer}
              onAddFlag={this.addFlagToPlayer}
              onDeleteFlag={this.deleteFlag}
              onAddVip={this.onAddVip}
              onDeleteVip={this.onDeleteVip}
              vips={this.state.vips}
            />
          )}
        </Grid>
      </Grid>
    );
  }
}

export default PlayersHistory;
export { FlagDialog, FlagButton, PlayersHistory };
