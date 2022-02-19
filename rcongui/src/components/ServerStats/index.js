import React from "react";
import ReactDOM from "react-dom";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  TimeSeriesScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  registerables,
} from "chart.js";
import StarIcon from "@material-ui/icons/Star";
import LinearProgress from "@material-ui/core/LinearProgress";
import Switch from "@material-ui/core/Switch";
import FormGroup from "@material-ui/core/FormGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormControl from "@material-ui/core/FormControl";
import MomentUtils from "@date-io/moment";
import { DateTimePicker, MuiPickersUtilsProvider } from "@material-ui/pickers";
import palette from "google-palette";
import "chartjs-adapter-moment";
import { Bar } from "react-chartjs-2";
import { makeStyles } from "@material-ui/core/styles";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import { fromJS } from "immutable";
import {
  Dialog,
  DialogTitle,
  Grid,
  Link,
  Modal,
  Typography,
  DialogContent,
  DialogActions,
  DialogContentText,
  Button,
  TextareaAutosize,
} from "@material-ui/core";

ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeSeriesScale,

  BarElement,
  Title,
  Tooltip,
  Legend
);

function hexToRgb(hex) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? "rgb(" +
        parseInt(result[1], 16) +
        "," +
        parseInt(result[2], 16) +
        "," +
        parseInt(result[3], 16) +
        ")"
    : null;
}

const useStyles = makeStyles((theme) => ({
  modal: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  paper: {
    backgroundColor: theme.palette.background.paper,
    border: "2px solid #000",
    boxShadow: theme.shadows[5],
    padding: theme.spacing(2, 4, 3),
  },
}));

function DetailsDialog({
  datasetElementIndex,
  datasetsIndex,
  dataPoint,
  unsetDatapoint,
  setPrevDataPoint,
  hasPrevDataPoint,
  setNextDataPoint,
  hasNextDataPoint,
}) {
  return (
    <Dialog
      open={
        datasetElementIndex !== null &&
        datasetsIndex !== null &&
        Object.keys(dataPoint).length > 0
      }
      onClose={unsetDatapoint}
    >
      <DialogTitle>{dataPoint.map}</DialogTitle>

      {datasetElementIndex !== null &&
      datasetsIndex !== null &&
      Object.keys(dataPoint).length > 0 ? (
        <React.Fragment>
          <DialogContent>
            <DialogContentText>
              {dataPoint.minute} - {dataPoint.count} players (
              {dataPoint.vip_count} VIPs)
            </DialogContentText>
            <ul>
              {dataPoint.players.map((el) => (
                <li key={el[1]}>
                  <Typography variant="body2">
                    <Link href={`#/player/${el[1]}`}> {el[0]}</Link>
                    {el[1]} {el[2] ? <StarIcon fontSize="inherit" /> : ""}
                  </Typography>
                </li>
              ))}
            </ul>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={setPrevDataPoint}
              disabled={!hasPrevDataPoint()}
              color="primary"
            >
              Prev
            </Button>
            <Button
              onClick={setNextDataPoint}
              disabled={!hasNextDataPoint()}
              color="primary"
            >
              Next
            </Button>
            <Button onClick={unsetDatapoint} color="primary">
              Close
            </Button>
          </DialogActions>
        </React.Fragment>
      ) : (
        "No data"
      )}
    </Dialog>
  );
}

function MetricsParams({
  from,
  setFrom,
  till,
  setTill,
  withPlayer,
  setWithPlayer,
  loadData,
  toggleShowControls,
}) {
  return (
    <Grid
      container
      alignContent="center"
      alignItems="center"
      justify="center"
      spacing={2}
    >
      <Grid item>
        <MuiPickersUtilsProvider utils={MomentUtils}>
          <DateTimePicker
            label="From time"
            format="YYYY/MM/DD HH:mm"
            value={from}
            onChange={setFrom}
          />
        </MuiPickersUtilsProvider>
      </Grid>
      <Grid item>
        <MuiPickersUtilsProvider utils={MomentUtils}>
          <DateTimePicker
            label="Till time"
            format="YYYY/MM/DD HH:mm"
            value={till}
            onChange={setTill}
          />
        </MuiPickersUtilsProvider>
      </Grid>
      <Grid item>
        <Grid container direction="column">
          <Link
            onClick={() => {
              setTill(new Date());
              setFrom(new Date(new Date() - 1 * 86400000));
            }}
          >
            Last 24h
          </Link>
          <Link
            onClick={() => {
              setTill(new Date());
              setFrom(new Date(new Date() - 3 * 86400000));
            }}
          >
            Last 72h
          </Link>
          <Link
            onClick={() => {
              setTill(new Date());
              setFrom(new Date(new Date() - 7 * 86400000));
            }}
          >
            Last 7d
          </Link>
        </Grid>
      </Grid>
      <Grid item>
        <FormControl component="fieldset">
          <FormGroup aria-label="position" row>
            <FormControlLabel
              value="With player list (slower load)"
              control={<Switch checked={withPlayer} onChange={setWithPlayer} />}
              label="With player list (slower load)"
              labelPlacement="top"
            />
          </FormGroup>
        </FormControl>
      </Grid>
      <Grid item>
        <Button onClick={loadData} variant="contained" color="primary">
          Load data
        </Button>
      </Grid>
      <Grid item>
        <Button onClick={toggleShowControls} variant="text">
          Hide controls
        </Button>
      </Grid>
    </Grid>
  );
}

const ServerStatsPage = ({ classes }) => {
  const [stats, setStats] = React.useState({});
  const [dataPoint, setDatapoint] = React.useState({});
  const [datasetsIndex, setDatasetsIndex] = React.useState(null);
  const [datasetElementIndex, setDatasetElementIndex] = React.useState(null);
  const [from, setFrom] = React.useState(new Date(new Date() - 1 * 86400000));
  const [till, setTill] = React.useState(new Date());
  const [withPlayer, _setWithPlayer] = React.useState(
    window.localStorage.getItem("stats_with_players") == "true"
  );
  const [dataLoading, setDataLoading] = React.useState(true);
  const [showControls, _setShowControls] = React.useState(
    window.localStorage.getItem("stats_show_controls") == "true"
  );

  const setWithPlayer = (event) => {
    _setWithPlayer(event.target.checked);
    window.localStorage.setItem("stats_with_players", event.target.checked);
  };

  const toggleShowControls = () => {
    const show = !showControls;
    _setShowControls(show);
    window.localStorage.setItem("stats_show_controls", show);
  };

  const colors = React.useMemo(
    () =>
      palette("tol-rainbow", stats ? Object.keys(stats).length : 10).map(
        function (hex) {
          const s = hexToRgb("#" + hex);
          console.log(s);
          return s;
        }
      ),
    [stats]
  );
  const styles = useStyles();
  const datasets = React.useMemo(
    () =>
      Object.keys(stats)
        .map((mapName, i) => ({
          grouped: false,
          label: mapName,
          data: stats[mapName],
          backgroundColor: colors[i],
          borderColor: colors[i],
          fill: true,
          parsing: {
            xAxisKey: "minute",
            yAxisKey: "count",
          },
        }))
        .concat(
          Object.keys(stats).map((mapName, i) => ({
            grouped: false,
            label: "vip",
            data: stats[mapName],
            parsing: {
              xAxisKey: "minute",
              yAxisKey: "vip_count",
            },
            backgroundColor: "#000000",
            borderColor: "#000000",
            fill: true,
          }))
        ),
    [stats, colors]
  );

  const unsetDatapoint = () => {
    setDatapoint({});
    setDatasetElementIndex(null);
    setDatasetsIndex(null);
  };

  const setDataPointFromIndex = (datasetIndex, index) => {
    const dataPoint = datasets[datasetIndex]?.data[index];
    if (!dataPoint) {
      return unsetDatapoint();
    }
    setDatapoint(dataPoint);
    setDatasetsIndex(datasetIndex);
    setDatasetElementIndex(index);
    console.log(dataPoint);
  };

  const hasNextDataPoint = () => {
    const nextDataPoint =
      datasets[datasetsIndex]?.data[datasetElementIndex + 1];
    if (!nextDataPoint) {
      return false;
    }
    if (new Date(nextDataPoint.minute) - new Date(dataPoint.minute) === 60000) {
      return true;
    }
    return false;
  };

  const hasPrevDataPoint = () => {
    const prevDataPoint =
      datasets[datasetsIndex]?.data[datasetElementIndex - 1];
    if (!prevDataPoint) {
      return false;
    }
    if (new Date(dataPoint.minute) - new Date(prevDataPoint.minute) === 60000) {
      return true;
    }
    return false;
  };

  const setNextDataPoint = () => {
    setDataPointFromIndex(datasetsIndex, datasetElementIndex + 1);
  };

  const setPrevDataPoint = () => {
    setDataPointFromIndex(datasetsIndex, datasetElementIndex - 1);
  };

  const loadData = () => {
    unsetDatapoint();
    setDataLoading(true);
    get(
      `get_server_stats?by_map=true&start=${from.toISOString()}&end=${till.toISOString()}&with_players=${+withPlayer}`
    )
      .then((res) => showResponse(res, "get_server_stats", false))
      .then((data) => {
        setDataLoading(false);
        return data.result && data.result ? setStats(data.result) : "";
      })
      .catch(handle_http_errors);
  };
  React.useEffect(() => {
    loadData();
  }, []);

  return stats ? (
    <React.Fragment>
      <DetailsDialog
        datasetElementIndex={datasetElementIndex}
        datasetsIndex={datasetsIndex}
        dataPoint={dataPoint}
        unsetDatapoint={unsetDatapoint}
        setPrevDataPoint={setPrevDataPoint}
        hasPrevDataPoint={hasPrevDataPoint}
        setNextDataPoint={setNextDataPoint}
        hasNextDataPoint={hasNextDataPoint}
      />
      <Grid container>
        <Grid item xs={12}>
          {showControls ? (
            <MetricsParams
              from={from}
              setFrom={setFrom}
              till={till}
              setTill={setTill}
              withPlayer={withPlayer}
              setWithPlayer={setWithPlayer}
              loadData={loadData}
              toggleShowControls={toggleShowControls}
            />
          ) : (
            <Link variant="text" size="small" onClick={toggleShowControls}>
              Show controls
            </Link>
          )}
        </Grid>
      </Grid>
      <Grid
        container
        spacing={2}
        className={classes.doublePadding}
        alignContent="center"
        alignItems="center"
        style={{ paddingTop: 0 }}
      >
        <Grid item xs={12}>
          {dataLoading ? <LinearProgress color="secondary" /> : ""}
        </Grid>
        <Grid item xs={12}>
          <Bar
            options={{
              onClick: (e, el) => {
                if (el.length > 0) {
                  console.log(el);
                  const clickedEl = el[0];
                  setDataPointFromIndex(
                    clickedEl.datasetIndex,
                    clickedEl.index
                  );
                }
              },
              plugins: {
                legend: {
                  labels: {
                    filter: function (item, chart) {
                      // Logic to remove a particular legend item goes here
                      return !item.text.includes("vip");
                    },
                  },
                },
                tooltip: {
                  callbacks: {
                    afterTitle: function (context) {
                      if (context && context[0]?.raw?.map) {
                        return context[0]?.raw?.map;
                      }
                      return "Can't get map info";
                    },
                    footer: function (context) {
                      if (context && context[0]?.raw?.players?.length > 0) {
                        return (
                          context[0]?.raw.players
                            .map((el) => el[0])
                            .slice(0, 10)
                            ?.join("\n") + "\n...\nClick for full list"
                        );
                      }

                      return "Player list not available";
                    },
                  },
                },
              },
              scales: {
                x: { type: "time", stacked: false },
                y: { min: 0, max: 100, stacked: false },
              },
            }}
            data={{
              datasets: datasets,
            }}
          />
        </Grid>
      </Grid>
    </React.Fragment>
  ) : (
    "No data"
  );
};

export default ServerStatsPage;
