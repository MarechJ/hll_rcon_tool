import React from "react";
import { range } from "lodash/util";
import {
  Grid,
  Typography,
  Button,
  TextField,
  Link,
  IconButton,
} from "@material-ui/core";
import {
  showResponse,
  postData,
  get,
  handle_http_errors,
  addPlayerToWatchList,
} from "../../utils/fetchUtils";
import Blacklist from "./blacklist";
import { toast } from "react-toastify";
import _ from "lodash";
import LinearProgress from "@material-ui/core/LinearProgress";
import Padlock from "../../components/SettingsView/padlock";
import WarningIcon from "@material-ui/icons/Warning";
import TextHistoryManager, { SelectNameSpace } from "./textHistoryManager";
import TextHistory from "../textHistory";
import ServicesList from "../Services";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import { ForwardCheckBox, WordList } from "../commonComponent";
import DeleteIcon from "@material-ui/icons/Delete";
import AddIcon from "@material-ui/icons/Add";
import SaveIcon from "@material-ui/icons/Save";
import { ManualPlayerInput } from "../commonComponent";
import { getSharedMessages } from "../../utils/fetchUtils";

const ManualWatchList = ({ classes }) => {
  const [name, setName] = React.useState("");
  const [steamId64, setSteamId64] = React.useState("");
  const [reason, setReason] = React.useState("");
  const [sharedMessages, setSharedMessages] = React.useState([]);

  React.useEffect(() => {
    getSharedMessages("punitions").then((data) => setSharedMessages(data));
  }, []);
  const textHistory = new TextHistory("watchlist");

  return (
    <ManualPlayerInput
      name={name}
      setName={setName}
      steam_id={steamId64}
      setSteamId={setSteamId64}
      reason={reason}
      setReason={setReason}
      textHistory={textHistory}
      sharedMessages={sharedMessages}
      classes={classes}
      actionName="Add"
      tooltipText="You will get a notification on you watchlist discord hook when this player enters your server"
      onSubmit={() => addPlayerToWatchList(steamId64, reason, null, name)}
    />
  );
};

const Hook = ({
  hook = "",
  roles = [],
  onAddHook,
  onDeleteHook,
  onUpdateHook,
  actionType,
}) => {
  const [myHook, setMyHook] = React.useState(hook);
  const [myRoles, setMyRoles] = React.useState(roles);
  console.log("Roles:", roles);
  return (
    <Grid container spacing={1}>
      <Grid item xs={4}>
        <TextField
          label="webhook url"
          fullWidth
          value={myHook}
          onChange={(e) => setMyHook(e.target.value)}
          helperText="Discord hook url"
        />
      </Grid>
      <Grid item xs={6}>
        <WordList
          label="Roles"
          helperText="Add roles to be pinged, hit enter to validate"
          placeholder="<@&111117777888889999>"
          words={myRoles}
          onWordsChange={setMyRoles}
        />
      </Grid>
      <Grid item xs={2}>
        {actionType === "delete" ? (
          <React.Fragment>
            <IconButton
              edge="start"
              onClick={() => onDeleteHook(myHook, myRoles)}
            >
              <DeleteIcon />
            </IconButton>
            <IconButton
              edge="start"
              onClick={() => onUpdateHook(myHook, myRoles)}
            >
              <SaveIcon />
            </IconButton>
          </React.Fragment>
        ) : (
          <IconButton edge="start" onClick={() => onAddHook(myHook, myRoles)}>
            <AddIcon />
          </IconButton>
        )}
      </Grid>
    </Grid>
  );
};

const WebhooksConfig = () => {
  const [hooks, setHooks] = React.useState([]);
  React.useEffect(() => {
    get("get_hooks")
      .then((res) => showResponse(res, "get_hooks", false))
      .then((res) => setHooks(res.result))
      .catch(handle_http_errors);
  }, []);

  const setHookConfig = (hookConfig) =>
    postData(`${process.env.REACT_APP_API_URL}set_hooks`, {
      name: hookConfig.name,
      hooks: hookConfig.hooks,
    })
      .then((res) => showResponse(res, `set_hooks ${hookConfig.name}`, true))
      .then((res) => setHooks(res.result))
      .catch(handle_http_errors);

  return (
    <React.Fragment>
      {hooks.map((hookConfig) => (
        <Grid container>
          <Grid item xs={12}>
            <Typography variant="h6" style={{ "text-transform": "capitalize" }}>
              For: {hookConfig.name}
            </Typography>
            <Grid container>
              {hookConfig.hooks.length ? (
                hookConfig.hooks.map((o, idx) => (
                  <Hook
                    hook={o.hook}
                    roles={o.roles}
                    actionType="delete"
                    onDeleteHook={() => {
                      hookConfig.hooks.splice(idx, 1);
                      setHookConfig(hookConfig);
                    }}
                    onUpdateHook={(hook, roles) => {
                      hookConfig.hooks[idx] = { hook: hook, roles: roles };
                      setHookConfig(hookConfig);
                    }}
                  />
                ))
              ) : (
                <Typography>{`No hooks defined for: ${hookConfig.name}`}</Typography>
              )}
            </Grid>
          </Grid>
          <Grid item xs={12}>
            <Hook
              actionType="add"
              onAddHook={(hook, roles) => {
                hookConfig.hooks.push({ hook: hook, roles: roles });
                setHookConfig(hookConfig);
              }}
            />
          </Grid>
        </Grid>
      ))}
    </React.Fragment>
  );
};

class RconSettings extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      broadcastMessages: [],
      standardMessages: [],
      standardMessagesType: "punitions",
      randomized: false,
      enabled: false,
    };

    this.loadBroadcastsSettings = this.loadBroadcastsSettings.bind(this);
    this.validate_messages = this.validate_messages.bind(this);
    this.saveBroadCastMessages = this.saveBroadCastMessages.bind(this);
    this.loadStandardMessages = this.loadStandardMessages.bind(this);
    this.saveStandardMessages = this.saveStandardMessages.bind(this);
    this.clearCache = this.clearCache.bind(this);
  }

  async loadBroadcastsSettings() {
    return get(`get_auto_broadcasts_config`)
      .then((res) => showResponse(res, "get_auto_broadcasts_config", false))
      .then(
        (data) =>
          !data.failed &&
          this.setState({
            broadcastMessages: data.result.messages,
            randomized: data.result.randomized,
            enabled: data.result.enabled,
          })
      )
      .catch(handle_http_errors);
  }

  async saveBroadcastsSettings(data) {
    return postData(
      `${process.env.REACT_APP_API_URL}set_auto_broadcasts_config`,
      data
    )
      .then((res) => showResponse(res, "set_auto_broadcasts_config", true))
      .then((res) => !res.failed && this.setState(data))
      .catch(handle_http_errors);
  }

  async loadStandardMessages() {
    return get(
      `get_standard_messages?message_type=${this.state.standardMessagesType}`
    )
      .then((res) => showResponse(res, "get_standard_messages", false))
      .then(
        (data) =>
          !data.failed &&
          this.setState({
            standardMessages: data.result,
          })
      )
      .catch(handle_http_errors);
  }

  async saveStandardMessages() {
    return postData(`${process.env.REACT_APP_API_URL}set_standard_messages`, {
      message_type: this.state.standardMessagesType,
      messages: this.state.standardMessages,
    })
      .then((res) => showResponse(res, "set_standard_messages", true))
      .then(this.loadStandardMessages)
      .catch(handle_http_errors);
  }

  async clearCache() {
    return postData(`${process.env.REACT_APP_API_URL}clear_cache`, {})
      .then((res) => showResponse(res, "clear_cache", true))
      .catch(handle_http_errors);
  }

  validate_messages() {
    let hasErrors = false;
    _.forEach(this.state.broadcastMessages, (m) => {
      const split = _.split(m, " ");

      if (_.isNaN(_.toNumber(split[0]))) {
        toast.error(`Invalid line, must start with number of seconds: ${m}`);
        hasErrors = true;
      }
    });
    return !hasErrors;
  }

  saveBroadCastMessages() {
    if (this.validate_messages()) {
      this.saveBroadcastsSettings({ messages: this.state.broadcastMessages });
    }
  }

  componentDidMount() {
    this.loadBroadcastsSettings();
    this.loadStandardMessages();
  }

  render() {
    const {
      broadcastMessages,
      standardMessages,
      standardMessagesType,
      enabled,
      randomized,
    } = this.state;
    const { classes, theme, themes, setTheme } = this.props;

    return (
      <Grid container className={classes.paper} spacing={3}>
        <Grid item xs={12}>
          <h2>Advanced RCON settings</h2>
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <Typography variant="h6">Your RCON color theme</Typography>
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <FormControl style={{ minWidth: "200px" }}>
            <InputLabel>Pick your theme</InputLabel>
            <Select
              value={theme}
              onChange={(event) => setTheme(event.target.value)}
            >
              {themes.map((t) => (
                <MenuItem key={t} value={t}>
                  {t}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <Typography variant="h6">Automated broadcast cycle</Typography>
        </Grid>
        <Grid item xs={12}>
          <Grid container justify="space-evenly">
            <Grid item>
              <Padlock
                handleChange={(v) =>
                  this.saveBroadcastsSettings({ enabled: v })
                }
                checked={enabled}
                label="Auto broadcast enabled"
              />
            </Grid>
            <Grid item>
              <Padlock
                handleChange={(v) =>
                  this.saveBroadcastsSettings({ randomized: v })
                }
                checked={randomized}
                label="Randomized messages"
              />
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Auto broadcast messages"
            multiline
            rows={8}
            value={_.join(
              broadcastMessages.map((m) => m.replace(/\n/g, "\\n")),
              "\n"
            )}
            onChange={(e) =>
              this.setState({
                broadcastMessages: _.split(e.target.value, "\n"),
              })
            }
            placeholder="Insert your messages here, one per line, with format: <number of seconds to display> <a message (write: \n if you want a line return)>"
            variant="outlined"
            helperText="You can use the following variables in the text (nextmap, maprotation, servername, vips, randomvip, ingame_mods, online_mods) using the following syntax: 60 Welcome to {servername}. The next map is {nextmap}."
          />
        </Grid>
        <Grid item xs={12}>
          <Button
            fullWidth
            onClick={this.saveBroadCastMessages}
            variant="outlined"
          >
            Save auto broadcast messages
          </Button>
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <Typography variant="h6">
            Manage your personal text history
          </Typography>
        </Grid>
        <Grid
          container
          spacing={1}
          alignContent="center"
          justify="center"
          alignItems="center"
          className={classes.root}
        >
          <Grid item xs={12} className={`${classes.padding} ${classes.margin}`}>
            <TextHistoryManager classes={classes} />
          </Grid>
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <Typography variant="h6">Manage shared standard messages</Typography>
        </Grid>
        <Grid item xs={12} className={classes.padding}>
          <SelectNameSpace
            value={standardMessagesType}
            handleChange={(v) =>
              this.setState(
                { standardMessagesType: v },
                this.loadStandardMessages
              )
            }
            values={["punitions", "welcome", "broadcast"]}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Shared standard messages"
            multiline
            rows={8}
            value={_.join(
              standardMessages.map((m) => m.replace(/\n/g, "\\n")),
              "\n"
            )}
            onChange={(e) =>
              this.setState({ standardMessages: _.split(e.target.value, "\n") })
            }
            placeholder="Set one message per line. If you want a line return in one of the message write: \n"
            variant="outlined"
            helperText="Set one message per line. If you want a line return in one of the message write: \n"
          />
        </Grid>
        <Grid item xs={12}>
          <Button
            fullWidth
            onClick={this.saveStandardMessages}
            variant="outlined"
          >
            Save shared messages
          </Button>
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Typography variant="h5">Blacklist player by Steam ID</Typography>
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Blacklist classes={classes} />
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Typography variant="h5">Add player to watchlist</Typography>
        </Grid>
        <Grid item xs={12}><ManualWatchList classes={classes} /></Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Typography variant="h5">Manage services</Typography>
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Grid container justify="center">
            <Grid item md={8} xs={12}>
              <ServicesList classes={classes} />
            </Grid>
          </Grid>
        </Grid>

        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Typography variant="h5">Discord Webhooks configuration</Typography>
        </Grid>
        <Grid
          item
          xs={12}
          className={`${classes.padding} ${classes.margin}`}
          alignContent="center"
          justify="center"
          alignItems="center"
          className={classes.root}
        >
          <WebhooksConfig classes={classes} />
        </Grid>
        <Grid item className={classes.paddingTop} justify="center" xs={12}>
          <Typography variant="h5">Misc. options</Typography>
        </Grid>
        <Grid
          item
          xs={12}
          className={`${classes.padding} ${classes.margin}`}
          alignContent="center"
          justify="center"
          alignItems="center"
          className={classes.root}
        >
          <Grid container justify="space-evenly">
            <Grid item>
              <Link href="/api/upload_vips" target="_blank">
                Bulk VIP upload / VIP export
              </Link>
            </Grid>
            <Grid item>
              <Link href="/api/scoreboard" target="_blank">
                Scoreboard (public link)
              </Link>
            </Grid>
            <Grid item>
              <Link href="/api/tk" target="_blank">
                Teamkills overview (public link)
              </Link>
            </Grid>
          </Grid>
        </Grid>
        <Grid
          item
          xs={12}
          className={`${classes.padding} ${classes.margin}`}
          alignContent="center"
          justify="center"
          alignItems="center"
          className={classes.root}
        >
          <Button
            color="secondary"
            variant="outlined"
            onClick={this.clearCache}
          >
            Clear application cache
          </Button>
        </Grid>
      </Grid>
    );
  }
}

export default RconSettings;
