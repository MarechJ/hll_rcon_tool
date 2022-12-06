import React from "react";
import "react-toastify/dist/ReactToastify.css";
import Grid from "@material-ui/core/Grid";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";

import debounce from "lodash/debounce";
import { useTheme } from "@material-ui/core/styles";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import Link from "@material-ui/core/Link";
import { fromJS, List } from "immutable";

const Status = ({ classes, name, nbPlayers, map, serverList }) => {
  const theme = useTheme();
  const isSmall = useMediaQuery(theme.breakpoints.down("sm"));
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <React.Fragment>
      <Grid container className={classes.alignLeft} spacing={1}>
        <Grid item>
          <Link variant="button" color="inherit" onClick={handleClick}>
            <strong
              style={{ display: "block" }}
              className={`${classes.ellipsis}`}
            >
              {isSmall ? `${name.substring(0, 40)}...` : name}
            </strong>
          </Link>
          <Menu
            id="simple-menu"
            anchorEl={anchorEl}
            keepMounted
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            {serverList.map((s) => {
              let link = `${window.location.protocol}//${
                window.location.hostname
              }:${s.get("port")}${window.location.pathname}${
                window.location.hash
              }`;
              if (s.get("link")) {
                link = `${s.get("link")}${window.location.pathname}${
                  window.location.hash
                }`;
              }
              return (
                <MenuItem onClick={handleClose}>
                  <Link color="inherit" href={link}>
                    {s.get("name")}
                  </Link>
                </MenuItem>
              );
            })}
          </Menu>
          <small style={{ display: "block" }}>
            {nbPlayers} - {map}
          </small>
        </Grid>
      </Grid>
    </React.Fragment>
  );
};

class ServerStatus extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      name: "",
      nbPlayers: "",
      map: "",
      serverList: List(),
      refreshIntervalSec: 10,
      listRefreshIntervalSec: 30,
      interval: null,
      intervalLoadList: null,
    };

    this.debouncedLoad = debounce(
      this.load.bind(this),
      this.state.refreshIntervalSec
    );
    this.debouncedLoadList = debounce(
      this.loadServerList.bind(this),
      this.state.listRefreshIntervalSec
    );
  }

  componentDidMount() {
    this.load();
    this.setState({
      interval: setInterval(
        this.debouncedLoad,
        this.state.refreshIntervalSec * 1000
      ),
    });
    this.setState({
      intervalLoadList: setInterval(
        this.debouncedLoadList,
        this.state.listRefreshIntervalSec * 1000
      ),
    });
    this.loadServerList();
  }

  componentWillUnmount() {
    clearInterval(this.state.interval);
    clearInterval(this.state.intervalLoadList);
  }

  async load() {
    return get(`get_status`)
      .then((response) => showResponse(response, "get_status", false))
      .then((data) => {
        this.setState({
          name: data.result.name,
          map: data.result.map,
          nbPlayers: data.result.nb_players,
        });
        document.title = `(${data.result.player_count}) ${data.result.short_name}`;
      })
      .catch(handle_http_errors);
  }

  async loadServerList() {
    return get(`server_list`)
      .then((response) => showResponse(response, "server_list", false))
      .then((data) => {
        this.setState({
          serverList: fromJS(data.result || []),
        });
      })
      .catch(handle_http_errors);
  }

  render() {
    const { map, name, nbPlayers, serverList } = this.state;
    const { classes } = this.props;

    return (
      <Status
        classes={classes}
        name={name}
        nbPlayers={nbPlayers}
        map={map}
        serverList={serverList}
      />
    );
  }
}

export default ServerStatus;
