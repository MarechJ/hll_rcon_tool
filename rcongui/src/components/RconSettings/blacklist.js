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
      steam_id: "",
      name: "",
      reason: "",
      sharedMessages: [],
    };

    this.blacklistPlayer = this.blacklistPlayer.bind(this);
  }

  async blacklistPlayer() {
    return postData(`${process.env.REACT_APP_API_URL}blacklist_player`, {
      steam_id_64: this.state.steam_id,
      name: this.state.name,
      reason: this.state.reason,
    })
      .then((res) => showResponse(res, "blacklist_player", true))
      .then(
        (res) =>
          !res.failed && this.setState({ steam_id: "", name: "", reason: "" })
      )
      .catch(handle_http_errors);
  }

  componentDidMount() {
    getSharedMessages("punitions").then((data) =>
      this.setState({ sharedMessages: data })
    );
  }

  render() {
    const { steam_id, name, reason, sharedMessages } = this.state;
    const { classes } = this.props;
    const textHistory = new TextHistory("punitions");

    return (
      <ManualPlayerInput
        name={name}
        setName={(val) => this.setState({ name: val })}
        steam_id={steam_id}
        setSteamId={(val) => this.setState({ steam_id: val })}
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
