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

const ServerStatsPage = ({ classes }) => {
  const [stats, setStats] = React.useState({});
  const [dataPoint, setDatapoint] = React.useState({});
  const [datasetsIndex, setDatasetsIndex] = React.useState(null);
  const [datasetElementIndex, setDatasetElementIndex] = React.useState(null);
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
      Object.keys(stats).map((mapName, i) => ({
        grouped: true,
        label: mapName,
        data: stats[mapName],
        backgroundColor: colors[i],
        borderColor: colors[i],
        fill: true,
      })),
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
      return unsetDatapoint()
    }
    setDatapoint(dataPoint);
    setDatasetsIndex(datasetIndex);
    setDatasetElementIndex(index);
    console.log(dataPoint);
  }
  
  const hasNextDataPoint = () => {
    const nextDataPoint = datasets[datasetsIndex]?.data[datasetElementIndex + 1];
    if (!nextDataPoint) {
      return false
    }
    if ((new Date(nextDataPoint.minute) - new Date(dataPoint.minute)) === 60000) {
      return true
    }
    return false
  }

  const hasPrevDataPoint = () => {
    const prevDataPoint = datasets[datasetsIndex]?.data[datasetElementIndex - 1];
    if (!prevDataPoint) {
      return false
    }
    if ((new Date(dataPoint.minute) - new Date(prevDataPoint.minute)) === 60000) {
      return true
    }
    return false
  }

  const setNextDataPoint = () => {
    setDataPointFromIndex(datasetsIndex, datasetElementIndex + 1)
  }

  const setPrevDataPoint = () => {
    setDataPointFromIndex(datasetsIndex, datasetElementIndex - 1)
  }

  React.useEffect(() => {
    unsetDatapoint();
    get(`get_server_stats`)
      .then((res) => showResponse(res, "get_server_stats?by_map=true", false))
      .then((data) => (data.result && data.result ? setStats(data.result) : ""))
      .catch(handle_http_errors);
  }, []);

  return stats ? (
    <React.Fragment>
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
              <DialogContentText>{dataPoint.minute}</DialogContentText>
              <ul>
                {dataPoint.players.map((el) => (
                  <li>
                    <Link href={`#/player/${el[1]}`}>{el[0]}</Link> {(el[1])}
                  </li>
                ))}
              </ul>
            </DialogContent>
            <DialogActions>
            <Button onClick={setPrevDataPoint} disabled={!hasPrevDataPoint()} color="primary">
                Prev
              </Button>
            <Button onClick={setNextDataPoint} disabled={!hasNextDataPoint()} color="primary">
                Next
              </Button>
              <Button onClick={unsetDatapoint}  color="primary">
                Close
              </Button>
            </DialogActions>
          </React.Fragment>
        ) : (
          "No data"
        )}
      </Dialog>
      <Bar
        options={{
          onClick: (e, el) => {
            if (el.length > 0) {
              console.log(el);
              const clickedEl = el[0];
              setDataPointFromIndex(clickedEl.datasetIndex, clickedEl.index)
            }
          },
          plugins: {
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
                      context[0]?.raw.players.map(el => el[0]).slice(0, 10)?.join("\n") +
                      "\n...\nClick for full list"
                    );
                  }

                  return "Can't get player list";
                },
              },
            },
          },
          scales: {
            x: { type: "time", stacked: true },
            y: { min: 0, max: 100, stacked: true },
          },
          parsing: {
            xAxisKey: "minute",
            yAxisKey: "count",
          },
        }}
        data={{
          datasets: datasets,
        }}
      />
    </React.Fragment>
  ) : (
    "No data"
  );
};

export default ServerStatsPage;
