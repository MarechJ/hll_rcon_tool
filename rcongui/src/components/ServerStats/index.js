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
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import { fromJS } from "immutable";
import { SportsRugbySharp } from "@material-ui/icons";

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

const ServerStatsPage = ({ classes }) => {
  const [stats, setStats] = React.useState({});
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
  
  const datasets = React.useMemo(() => Object.keys(stats).map((mapName, i) => ({
    grouped: true,
    label: mapName,
    data: stats[mapName],
    backgroundColor: colors[i],
    borderColor: colors[i],
    fill: true,
  })), [stats, colors])

  React.useEffect(() => {
    get(`get_server_stats`)
      .then((res) => showResponse(res, "get_server_stats?by_map=true", false))
      .then((data) => (data.result && data.result ? setStats(data.result) : ""))
      .catch(handle_http_errors);
  }, []);

  console.log("Stats: ", stats);
  return stats ? (
    <Bar
      options={{
        onClick: (e, el) => {
          if (el.length > 0) {
            console.log(el)
            const clickedEl = el[0]
            const dataPoint = datasets[clickedEl.datasetIndex].data[clickedEl.index]
            console.log(dataPoint)
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
                    context[0]?.raw.players.slice(0, 10)?.join("\n") +
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
  ) : (
    "No data"
  );
};

export default ServerStatsPage;
