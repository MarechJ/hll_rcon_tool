import React from "react";
import {
  getSharedMessages,
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";
import TextHistory from "../textHistory";
import { ManualPlayerInput } from "../commonComponent";

class Blacklist extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      playerId: "",
      name: "",
      reason: "",
      sharedMessages: [],
    };

    this.blacklistPlayer = this.blacklistPlayer.bind(this);
  }

  async blacklistPlayer() {
    return postData(`${process.env.REACT_APP_API_URL}blacklist_player`, {
      playerId: this.state.playerId,
      name: this.state.name,
      reason: this.state.reason,
    })
      .then((res) => showResponse(res, "blacklist_player", true))
      .then(
        (res) =>
          !res.failed && this.setState({ playerId: "", name: "", reason: "" })
      )
      .catch(handle_http_errors);
  }

  componentDidMount() {
    getSharedMessages("punishments").then((data) =>
      this.setState({ sharedMessages: data })
    );
  }

  render() {
    const { playerId, name, reason, sharedMessages } = this.state;
    const { classes } = this.props;
    const textHistory = new TextHistory("punishments");

    return (
      <ManualPlayerInput
        name={name}
        setName={(val) => this.setState({ name: val })}
        playerId={playerId}
        setPlayerId={(val) => this.setState({ playerId: val })}
        reason={reason}
        setReason={(val) => this.setState({ reason: val })}
        textHistory={textHistory}
        sharedMessages={sharedMessages}
        tooltipText="Blacklisted players will instantly be banned when entering the server."
        onSubmit={this.blacklistPlayer}
        actionName="Blacklist"
        classes={classes}
      />
    );
  }
}

export default Blacklist;
