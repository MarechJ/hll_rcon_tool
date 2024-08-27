import React from "react";
import {
  Grid,
  Tab,
  Tabs,
  useTheme,
  useMediaQuery,
  Container,
} from "@material-ui/core";
import { Link, Switch, Route } from "react-router-dom";
import VoteMapConfig from "./votemap/votemap";
import MapRotationConfig from "./map-rotation/map-rotation";
import MapChange from "./map-change/map-change";

const tabs = {
  change: 0,
  rotation: 1,
  objectives: 2,
  votemap: 3,
};

export function MapManager({ match }) {
  const theme = useTheme();
  const isMdScreen = useMediaQuery(theme.breakpoints.up("md"));
  let location = match.params.path;

  return (
    <Container maxWidth="xl" style={{ padding: theme.spacing(2) }}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={true}>
          <Tabs
            orientation={isMdScreen ? "vertical" : "horizontal"}
            variant={!isMdScreen ? "scrollable" : "fullWidth"}
            value={tabs[location]}
            aria-label="nav tabs example"
            scrollButtons="on"
          >
            <LinkTab label="Map Change" to="change" {...a11yProps(0)} />
            <LinkTab label="Rotation" to="rotation" {...a11yProps(1)} />
            <LinkTab label="Objectives" to="objectives" {...a11yProps(2)} />
            <LinkTab label="Votemap" to="votemap" {...a11yProps(3)} />
          </Tabs>
        </Grid>
        <Grid item xs={12} md={10}>
          <Switch>
            <TabPanel path={"/settings/maps/change"} index={0}>
              <MapChange />
            </TabPanel>
            <TabPanel path={"/settings/maps/rotation"} index={1}>
              <MapRotationConfig />
            </TabPanel>
            <TabPanel path={"/settings/maps/objectives"} index={2}>
              <h1>TODO - OBJECTIVES</h1>
            </TabPanel>
            <TabPanel path={"/settings/maps/votemap"} index={3}>
              <VoteMapConfig />
            </TabPanel>
          </Switch>
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
