import React, { Component } from "react";
import "react-toastify/dist/ReactToastify.css";
import {
  addPlayerToBlacklist,
  get,
  getBlacklists,
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";
import AutoRefreshBar from "./header";
import TextInputBar from "./textInputBar";
import CompactList from "./playerList";
import Chip from "@material-ui/core/Chip";
import { ReasonDialog } from "./playerActions";
import GroupActions from "./groupActions";
import Unban from "./unban";
import { fromJS, List } from "immutable";
import { FlagDialog } from "../PlayersHistory";
import { getEmojiFlag } from "../../utils/emoji";
import BlacklistRecordCreateDialog from "../Blacklist/BlacklistRecordCreateDialog";

function stripDiacritics(string) {
  return typeof string.normalize !== "undefined"
    ? string.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    : string;
}

const PlayerSummary = ({ player, flag }) => {
  return player ? (
    <React.Fragment>
      <p>
        Add flag: {flag ? getEmojiFlag(flag) : <small>Please choose</small>}
      </p>
      <p>
        To:{" "}
        {player.get("names")
          ? player.get("names", []).map((n) => <Chip label={n.get("name")} />)
          : "No name recorded"}
      </p>
      <p>Player ID: {player.get("player_id", "")}</p>
    </React.Fragment>
  ) : (
    ""
  );
};

class PlayerView extends Component {
  constructor(props) {
    super();
    this.state = {
      selectedPlayers: new List(),
      bannedPlayers: null,
      players: new List(),
      filteredPlayers: new List(),
      filter: "",
      filterTimeout: null,
      actionMessage: "",
      doConfirm: false,
      sortType: localStorage.getItem("player_sort")
        ? localStorage.getItem("player_sort")
        : "",
      openGroupAction: false,
      openUnban: false,
      flag: false,
      blacklistOpen: false,
      blacklists: [],
      blacklistTarget: null,
    };

    this.onPlayerSelected = this.onPlayerSelected.bind(this);
    this.filterPlayers = this.filterPlayers.bind(this);
    this.filterChange = this.filterChange.bind(this);
    this.loadPlayers = this.loadPlayers.bind(this);
    this.handleAction = this.handleAction.bind(this);
    this.loadBans = this.loadBans.bind(this);
    this.unBan = this.unBan.bind(this);
    this.addFlagToPlayer = this.addFlagToPlayer.bind(this);
    this.deleteFlag = this.deleteFlag.bind(this);
    this.blacklistPlayer = this.blacklistPlayer.bind(this)
    this.handleBlacklistOpen = this.handleBlacklistOpen.bind(this)
    this.sortTypeChange = this.sortTypeChange.bind(this);
  }

  addFlagToPlayer(playerObj, flag, comment = null) {
    return postData(`${process.env.REACT_APP_API_URL}flag_player`, {
      player_id: playerObj.get("player_id"),
      flag: flag,
      comment: comment,
    })
      .then((response) => showResponse(response, "flag_player", true))
      .then(() => this.setState({ flag: false }))
      .then(this.loadPlayers)
      .catch(handle_http_errors);
  }

  deleteFlag(flag_id) {
    return postData(`${process.env.REACT_APP_API_URL}unflag_player`, {
      flag_id: flag_id,
    })
      .then((response) => showResponse(response, "unflag_player", true))
      .then(this.loadPlayers)
      .catch(handle_http_errors);
  }

  blacklistPlayer(payload) {
    addPlayerToBlacklist(payload)
  }
  
  async handleBlacklistOpen(player) {
    const blacklists = await getBlacklists();
    this.setState({ blacklists, blacklistOpen: true, blacklistTarget: player })
  }

  unBan(ban) {
    postData(`${process.env.REACT_APP_API_URL}unban`, {
      player_id: ban.player_id,
    })
      .then((response) =>
        showResponse(response, `Remove ${ban.type} ban for ${ban.name}`, true)
      )
      .then(this.loadBans)
      .catch(handle_http_errors);
  }

  handleAction(
    actionType,
    player_name,
    message = null,
    comment = null,
    duration_hours = 2,
    player_id = null,
    save_message = true
  ) {
    if (message === null) {
      message = this.state.actionMessage;
    }

    if (
      message === "" &&
      !actionType.startsWith("switch_") &&
      !actionType.startsWith("unwatch_")
    ) {
      this.setState({
        doConfirm: {
          player: player_name,
          actionType: actionType,
          player_id: player_id,
        },
      });
    } else {
      const data = {
        player_name: player_name,
        player_id: player_id,
        reason: message,
        comment: comment,
        duration_hours: duration_hours,
        message: message,
        save_message: save_message,
      };

      postData(`${process.env.REACT_APP_API_URL}${actionType}`, data)
        .then((response) =>
          showResponse(response, `${actionType} ${player_name}`, true)
        )
        .then(this.loadPlayers)
        .catch(handle_http_errors);
    }
    // Work around to the fact that the player ID is not always know in this scope (as is changes the behaviour of the temp / perma ban commands)
    if (comment) {
      let playerId = player_id;
      if (!playerId) {
        try {
          console.log(this.state.players);
          playerId = this.state.players
            .filter((p) => p.get("name") === player_name)
            .get(0)
            .get("player_id");
          console.log(playerId);
        } catch (err) {
          console.log("Unable to get player ID", err);
        }
      }
      postData(`${process.env.REACT_APP_API_URL}post_player_comment`, {
        player_id: playerId,
        comment: comment,
      })
        .then((response) =>
          showResponse(response, `post_player_comment ${player_name}`, true)
        )
        .then(this.loadPlayers)
        .catch(handle_http_errors);
    }
  }

  onPlayerSelected(players) {
    this.setState({ selectedPlayers: players });
  }

  async load(command, callback) {
    return get(command)
      .then((response) => showResponse(response, command))
      .then((data) => callback(data))
      .catch(handle_http_errors);
  }

  loadPlayers() {
    return this.load("get_players", (data) => {
      this.setState(
        { players: data.result === null ? new List() : fromJS(data.result) },
        () => {
          this.filterPlayers();
        }
      );
      return data;
    });
  }

  loadBans() {
    return this.load("get_bans", (data) =>
      this.setState({ bannedPlayers: data.result })
    );
  }

  filterChange(filter) {
    clearTimeout(this.state.filterTimeout); // switch to lodash debounce
    this.setState({
      filter: filter,
      filterTimeout: setTimeout(this.filterPlayers, 200),
    });
  }

  filterPlayers() {
    const { filter, players } = this.state;

    if (filter) {
      const filteredPlayers = players.filter(
        (p) =>
          stripDiacritics(p.get("name"))
            .toLowerCase()
            .indexOf(filter.toLowerCase()) >= 0
      );
      this.setState({ filteredPlayers: filteredPlayers });
    }

    if (!filter) {
      this.setState({ filteredPlayers: players });
    }
  }

  sortTypeChange(sortType) {
    this.setState({ sortType });
    localStorage.setItem("player_sort", sortType);
  }

  componentDidMount() {
    this.loadPlayers();
  }
  render() {
    const { classes, isFullScreen, onFullScreen } = this.props;
    const {
      openGroupAction,
      openUnban,
      players,
      filteredPlayers,
      actionMessage,
      doConfirm,
      sortType,
      bannedPlayers,
      flag,
      blacklistOpen,
      blacklists,
      blacklistTarget,
    } = this.state;

    return (
      <React.Fragment>
        <AutoRefreshBar
          intervalFunction={this.loadPlayers}
          everyMs={15000}
          refreshIntevalMs={100}
          onGroupActionClick={() => this.setState({ openGroupAction: true })}
          onUnbanClick={() => {
            this.loadBans();
            this.setState({ openUnban: true });
          }}
          isFullScreen={isFullScreen}
          onFullScreenClick={onFullScreen}
        />
        <TextInputBar
          classes={classes}
          handleChange={this.filterChange}
          total={players.size}
          showCount={filteredPlayers.size}
          handleMessageChange={(text) => this.setState({ actionMessage: text })}
          actionMessage={actionMessage}
          sortType={sortType}
          handleSortTypeChange={this.sortTypeChange}
        />

        <CompactList
          classes={classes}
          sortType={sortType}
          players={filteredPlayers}
          handleAction={(
            actionType,
            player,
            message = null,
            comment = null,
            duration_hours = 2,
            player_id = null
          ) =>
            this.handleAction(
              actionType,
              player,
              message,
              comment,
              duration_hours,
              player_id
            )
          }
          handleToggle={() => 1}
          onFlag={(player) => this.setState({ flag: player })}
          onDeleteFlag={(flagId) => this.deleteFlag(flagId)}
          onBlacklist={this.handleBlacklistOpen}
        />

        <GroupActions
          onClose={() => this.setState({ openGroupAction: false })}
          open={openGroupAction}
          classes={classes}
          players={players} /* Todo handle immuatable */
          handleAction={this.handleAction}
        />
        <Unban
          open={openUnban}
          onReload={this.loadBans}
          handleUnban={this.unBan}
          bannedPlayers={bannedPlayers}
          classes={classes}
          onClose={() => this.setState({ openUnban: false })}
        />
        <ReasonDialog
          open={doConfirm}
          handleClose={() => this.setState({ doConfirm: false })}
          handleConfirm={(
            action,
            player,
            reason,
            comment,
            duration_hours = 2,
            player_id = null
          ) => {
            this.handleAction(
              action,
              player,
              reason,
              comment,
              duration_hours,
              player_id
            );
            this.setState({ doConfirm: false });
          }}
        />
        <FlagDialog
          open={flag}
          handleClose={() => this.setState({ flag: false })}
          handleConfirm={this.addFlagToPlayer}
          SummaryRenderer={PlayerSummary}
        />
        <BlacklistRecordCreateDialog
          open={blacklistOpen}
          blacklists={blacklists}
          initialValues={blacklistTarget && { playerId: blacklistTarget.get("player_id") }}
          onSubmit={this.blacklistPlayer}
          setOpen={() => this.setState({ blacklistOpen: !blacklistOpen })}
          disablePlayerId={true}
        />
      </React.Fragment>
    );
  }
}

export default PlayerView;
