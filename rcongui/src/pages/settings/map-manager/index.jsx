import React from "react";
import { Tab, Tabs, useTheme, useMediaQuery } from "@mui/material";
import Grid from "@mui/material/Grid2"
import { makeStyles } from '@mui/styles';
import { Link, Outlet, Route, useLocation } from "react-router-dom";
import { get, getGameState } from "../../../utils/fetchUtils.js";

const tabs = {
  change: 0,
  rotation: 1,
  objectives: 2,
  votemap: 3,
};

const useStyles = makeStyles((theme) => ({
  container: {
  },
  main: {
    maxWidth: theme.breakpoints.values.md,
  },
  page: {
    marginTop: theme.spacing(3),
  },
  tabs: {
    // margin: -theme.spacing(2),
    marginBottom: theme.spacing(1),
    [theme.breakpoints.up("md")]: {
      marginRight: theme.spacing(2),
    },
  },
}));

const UPDATE_INTERVAL = 60 * 1000;

function MapManager({ match }) {
  const theme = useTheme();
  const classes = useStyles();
  const isMdScreen = useMediaQuery(theme.breakpoints.up("md"));
  const [gameState, setGameState] = React.useState(null);
  const [maps, setMaps] = React.useState([]);
  const statusIntervalRef = React.useRef(null);
  
  const pathRoot = '/settings/maps';

  const location = useLocation();

  const currentTab = location?.pathname ?? '';

  const updateGameState = async () => {
    const state = await getGameState();
    if (state) {
      setGameState(state);
    }
  };

  const getMaps = async () => {
    const response = await get("get_maps");
    const data = await response.json();
    const mapLayers = data.result;
    if (mapLayers) {
      setMaps(mapLayers);
    }
  };

  React.useEffect(() => {
    updateGameState();
    getMaps();
    statusIntervalRef.current = setInterval(updateGameState, UPDATE_INTERVAL);
    return () => clearInterval(statusIntervalRef.current);
  }, []);

  return (
    (<Grid container>
      <Grid size={{
        xs: 12,
        md: 2,
      }}>
        <Tabs
          orientation={isMdScreen ? "vertical" : "horizontal"}
          variant={!isMdScreen ? "scrollable" : "fullWidth"}
          value={currentTab}
          aria-label="nav tabs example"
          className={classes.tabs}
        >
          <LinkTab label="Map Change" to={pathRoot + "/change"} {...a11yProps(0)} />
          <LinkTab label="Rotation" to={pathRoot + "/rotation"} {...a11yProps(1)} />
          <LinkTab label="Objectives" to={pathRoot + "/objectives"} {...a11yProps(2)} />
          <LinkTab label="Votemap" to={pathRoot + "/votemap"} {...a11yProps(3)} />
        </Tabs>
      </Grid>
      <Grid className={classes.main} size={{
        xs: 12,
        md: 8,
      }}>
        <Outlet context={{ maps }} />
      </Grid>
    </Grid>)
  );
}

function LinkTab(props) {
  return <Tab component={Link} {...props} />;
}

function TabPanel(props) {
  const { children, path, index, ...other } = props;

  return (
    <Route
      role="tabpanel"
      hidden={tabs[path] !== index}
      id={`maps-tabpanel-${index}`}
      aria-labelledby={`maps-tab-${index}`}
      {...other}
    >
      {children}
    </Route>
  );
}

function a11yProps(index) {
  return {
    id: `nav-tab-${index}`,
    "aria-controls": `nav-tabpanel-${index}`,
  };
}

export default MapManager;
