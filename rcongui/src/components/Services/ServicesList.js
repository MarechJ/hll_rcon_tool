import React from "react";
import ListItemText from "@mui/material/ListItemText";
import "react-toastify/dist/ReactToastify.css";
import { fromJS, List as IList } from "immutable";
import Typography from "@mui/material/Typography";
import Switch from "@mui/material/Switch";
import Chip from "@mui/material/Chip";
import { get, postData, showResponse } from "../../utils/fetchUtils";
import Grid from "@mui/material/Grid2";

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

const Process = ({
  name,
  description,
  upTime,
  status,
  isOn,
  onToggle,
}) => (
  <Grid
    container
    justifyContent="space-around"
    spacing={1}
  >
    <Grid spacing={1} size={12}>
      <Grid container>
        <Grid size={6}>
          <Grid
            container
          >
            <Grid size={12}>
              <Typography
                variant="h6"
              >
                {name}
              </Typography>
              <ListItemText
                primary=""
                secondary={description}
                
              />
            </Grid>
          </Grid>
        </Grid>
        <Grid size={4}>
          <Chip label={status} color={StatusToColor[status]} />
          <ListItemText
            primary=""
            secondary={upTime}
            
          />
        </Grid>
        <Grid size={2}>
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
    this.poll = this.poll.bind(this);
  }

  poll() {
    const handle = setTimeout(
      () => this.getServices().then(this.poll),
      1000 * 10
    );
    return this.setState({ pollHandle: handle });
  }

  componentDidMount() {
    this.getServices();
    this.poll();
  }

  componentWillUnmount() {
    clearTimeout(this.state.pollHandle);
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
    }).then((res) => showResponse(res, "do_service", true));
  }

  isOK(processInfo) {
    return (
      processInfo.get("statename") === "RUNNING" ||
      processInfo.get("statename") === "STARTING"
    );
  }

  render() {
    const { services } = this.state;

    return (
      (<Grid container spacing={1}>
        <Grid size={12}>
          {services.map((s) => (
            <Process
              
              name={s.get("name")}
              description={s.get("info")}
              status={s.get("statename")}
              upTime={s.get("description", " , ").split(",")[1]}
              isOn={this.isOK(s)}
              onToggle={() =>
                this.toggleService(s.get("name"), !this.isOK(s)).then(
                  this.getServices
                )
              }
            />
          ))}
        </Grid>
      </Grid>)
    );
  }
}

export default ServicesList;
