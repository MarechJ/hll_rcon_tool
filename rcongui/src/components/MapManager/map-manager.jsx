import React from "react";
import { get } from "../../utils/fetchUtils";
import ChangeMap from "../SettingsView/changeMap";
import { Box, Grid, Tab, Tabs, Typography, useTheme, useMediaQuery } from "@material-ui/core";
import { Link, useLocation, Switch, Route } from "react-router-dom";
import MapRotation from ".";
import VoteMapConfig from "../SettingsView/voteMapConfig";
import MapRotationSettings from "./settings";

const tabs = {
  "change": 0,
  "rotation": 1,
  "objectives": 2,
  "votemap": 3,
};

export function MapManager({ match }) {
  const [maps, setMaps] = React.useState([]);
  const theme = useTheme();
  const isMdScreen = useMediaQuery(theme.breakpoints.up('md'));
  let location = match.params.path

  React.useEffect(() => {
    get("get_maps")
      .then((res) => res.json())
      .then((data) => setMaps(data.result));
  }, []);

  return (
    <div style={{ textAlign: "left", padding: "0 1.5rem" }}>
      <Grid container>
        <Grid item xs={12} md={3} lg={2}>
          <h1>Map Manager</h1>
          <Tabs
            orientation={isMdScreen ? "vertical" : "horizontal"}
            variant={!isMdScreen && "scrollable"}
            scrollButtons="on"
            value={tabs[location]}
            aria-label="nav tabs example"
          >
            <LinkTab label="Map Change" to="change" {...a11yProps(0)} />
            <LinkTab label="Rotation" to="rotation" {...a11yProps(1)} />
            <LinkTab label="Objectives" to="objectives" {...a11yProps(2)} />
            <LinkTab label="Votemap" to="votemap" {...a11yProps(3)} />
          </Tabs>
        </Grid>
        <Grid item xs={12} md={9} lg={10}>
            <Switch>
                <TabPanel path={"/settings/maps/change"} index={0}>
                    Page One
                </TabPanel>
                <TabPanel path={"/settings/maps/rotation"} index={1}>
                  <MapRotation classes={{}} />
                  <MapRotationSettings classes={{}} />
                </TabPanel>
                <TabPanel path={"/settings/maps/objectives"} index={2}>
                    Page Three
                </TabPanel>
                <TabPanel path={"/settings/maps/votemap"} index={3}>
                    <VoteMapConfig />
                </TabPanel>
            </Switch>
        </Grid>
      </Grid>
    </div>
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
