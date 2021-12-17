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
} from "chart.js";
import "chartjs-adapter-moment";
import { Bar } from "react-chartjs-2";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import { fromJS } from "immutable";

ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeSeriesScale,

  BarElement,
  Title,
  Tooltip,
  Legend
);

const ServerStatsPage = ({ classes }) => {
  const [stats, setStats] = React.useState([]);

  React.useEffect(() => {
    get(`get_server_stats`)
      .then((res) => showResponse(res, "get_server_stats", false))
      .then((data) => (data.result && data.result ? setStats(data.result) : ""))
      .catch(handle_http_errors);
  }, []);

  console.log("Stats: ", stats);
  return stats.length > 0 ? (
    <Bar
      options={{
        plugins: {
          tooltip: {
            callbacks: {
              afterTitle: function (context) {
                if (context && context[0]?.raw?.map) {
                    return context[0]?.raw?.map
                }
                return "Can't get map info"
              },
              footer: function (context) {
                if (context && context[0]?.raw?.players?.length > 0) {
                  console.log("here")
                  return context[0]?.raw.players.slice(0, 10)?.join('\n') + '\n...\nClick for full list'
                
                }
                
                return "Can't get player list";
              },
            },
          },
        },
        scales: {
          x: { type: "time" },
          y: { min: 0, max: 100 },
        },
        parsing: {
          xAxisKey: "minute",
          yAxisKey: "count",
        },
      }}
      data={{
        datasets: [
          {
            label: "PlayerCount",
            data: stats,
            backgroundColor: "rgb(255, 99, 132)",
            borderColor: "rgb(255, 99, 132)",
          },
        ],
      }}
    />
  ) : (
    "No data"
  );
};

export default ServerStatsPage;
