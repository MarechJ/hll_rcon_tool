import React, { Component } from "react";
import List from "@material-ui/core/List";
import { Grid } from "@material-ui/core";
import ListItem from "@material-ui/core/ListItem";
import ListItemSecondaryAction from "@material-ui/core/ListItemSecondaryAction";
import ListItemText from "@material-ui/core/ListItemText";
import _ from "lodash";
import "react-toastify/dist/ReactToastify.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faLock,
  faQuestionCircle,
  faExclamationCircle,
  faStar,
} from "@fortawesome/free-solid-svg-icons";
import { faSteam } from "@fortawesome/free-brands-svg-icons";
import Link from "@material-ui/core/Link";
import withWidth from "@material-ui/core/withWidth";
import Icon from "@material-ui/core/Icon";
import OpenInNewIcon from "@material-ui/icons/OpenInNew";
import { getEmojiFlag } from "../../utils/emoji";
import { Map, List as IList, fromJS } from "immutable";
import ScheduleIcon from "@material-ui/icons/Schedule";
import { Emoji } from "emoji-mart";
import LockIcon from "@material-ui/icons/Lock";
import { getName } from "country-list";
import Popover from "@material-ui/core/Popover";
import Typography from "@material-ui/core/Typography";
import { makeStyles } from "@material-ui/core/styles";
import { sumBy } from "lodash/math";
import { toPairs } from "lodash/object";
import Switch from "@material-ui/core/Switch";
import Chip from "@material-ui/core/Chip";
import Divider from "@material-ui/core/Divider";
import {
  postData,
  showResponse,
  handle_http_errors,
  sendAction,
  get,
} from "../../utils/fetchUtils";

const StatusToColor = {
  RUNNING: "primary",
  STARTING: "primary",
  STOPPED: "default",
  STOPPING: "default",
  BACKOFF: "secondary",
  EXITED: "secondary",
  FATAL: "secondary",
  UNKNOWN: "secondary",
};

const Process = ({ name, description, status, isOn, onToggle, classes }) => (
  <Grid
    container
    justify="space-around"
    spacing={1}
    className={classes.padding}
  >
    <Grid item xs={12} spacing={1}>
      <Grid container>
        <Grid item xs={6}>
          <Grid
            container
            className={`${classes.alignLeft} ${classes.noPaddingMarginBottom}`}
          >
            <Grid item xs={12}>
              <Typography
                className={classes.noPaddingMarginBottom}
                variant="h6"
              >
                {name}
              </Typography>
              <ListItemText
                primary=""
                secondary={description}
                className={classes.noPaddingMargin}
              />
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={4}>
          <Chip label={status} color={StatusToColor[status]} />
        </Grid>
        <Grid item xs={2}>
          <Switch checked={isOn} onChange={onToggle} name="Start/Stop" />
        </Grid>
      </Grid>
    </Grid>
  </Grid>
);

class ServicesList extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      services: IList(),
      pollHandle: null, 
    };

    this.getServices = this.getServices.bind(this);
    this.toggleService = this.toggleService.bind(this);
    this.isOK = this.isOK.bind(this);
  }

  poll() {
    const handle = setTimeout(this.getServices().then(this.poll), 1000 * 10)
    return this.setState({pollHandle: handle})
  }

  componentDidMount() {
    this.getServices();    
  }

  componentWillUnmount() {
      clearTimeout(this.state.pollHandle)
  }

  async getServices() {
    return get(`get_services`)
      .then((res) => showResponse(res, "get_services", false))
      .then((res) =>
        res.result ? this.setState({ services: fromJS(res.result) }) : ""
      );
  }

  async toggleService(serviceName, start) {
    return postData(`${process.env.REACT_APP_API_URL}do_service`, {
      service_name: serviceName,
      action: start ? "START" : "STOP",
    }).then(res => showResponse(res, "do_service", true));
  }

  isOK(processInfo) {
    return processInfo.get("statename") === "RUNNING" || processInfo.get("statename") === "STARTING"
  }

  render() {
    const { services } = this.state;
    const { classes } = this.props;

    return (
      <Grid container spacing={1}>
        <Grid item xs={12}>
          {services.map((s) => (
            <Process
              classes={classes}
              name={s.get("name")}
              description={s.get("info")}
              status={s.get("statename")}
              isOn={this.isOK(s)}
              onToggle={() =>
                this.toggleService(
                  s.get("name"),
                  !this.isOK(s)
                ).then(this.getServices)
              }
            />
          ))}
        </Grid>
      </Grid>
    );
  }
}

export default ServicesList;
