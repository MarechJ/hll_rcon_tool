import React from "react";
import { Grid, Tab, Tabs, useTheme, useMediaQuery, Container, Box } from "@mui/material";
import makeStyles from '@mui/styles/makeStyles';
import { Link, Switch, Route } from "react-router-dom";
import VoteMapConfig from "./votemap/index.jsx";
import MapRotationConfig from "./map-rotation";
import MapChange from "./map-change";
import MapObjectives from "./objectives";
import { MapState } from "./map-state.jsx";
import { get, getGameState } from "../../utils/fetchUtils.js";

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

export function MapManager({ match }) {
  const theme = useTheme();
  const classes = useStyles();
  const isMdScreen = useMediaQuery(theme.breakpoints.up("md"));
  const [gameState, setGameState] = React.useState(null);
  const [maps, setMaps] = React.useState([]);
  const statusIntervalRef = React.useRef(null);
  let location = match.params.path;

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
    <Container maxWidth="xl" className={classes.container}>
      <Grid container>
        <Grid xs={12} md={true}>
          <Tabs
            orientation={isMdScreen ? "vertical" : "horizontal"}
            variant={!isMdScreen ? "scrollable" : "fullWidth"}
            value={tabs[location]}
            aria-label="nav tabs example"
            scrollButtons
            allowScrollButtonsMobile>
            <LinkTab label="Map Change" to="change" {...a11yProps(0)} />
            <LinkTab label="Rotation" to="rotation" {...a11yProps(1)} />
            <LinkTab label="Objectives" to="objectives" {...a11yProps(2)} />
            <LinkTab label="Votemap" to="votemap" {...a11yProps(3)} />
          </Tabs>
        </Grid>
        <Grid xs={12} md={10}>
          <Box className={classes.main}>
            <MapState gameState={gameState} />
            <Box className={classes.page}>
              <Switch>
                <TabPanel path={"/settings/maps/change"} index={0}>
                  <MapChange maps={maps} />
                </TabPanel>
                <TabPanel path={"/settings/maps/rotation"} index={1}>
                  <MapRotationConfig maps={maps} />
                </TabPanel>
                <TabPanel path={"/settings/maps/objectives"} index={2}>
                  <MapObjectives />
                </TabPanel>
                <TabPanel path={"/settings/maps/votemap"} index={3}>
                  <VoteMapConfig maps={maps} />
                </TabPanel>
              </Switch>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </Container>
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
