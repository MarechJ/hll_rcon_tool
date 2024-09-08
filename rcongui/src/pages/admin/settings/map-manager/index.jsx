import React from "react";
import { Outlet } from "react-router-dom";
import { get, getGameState } from "@/utils/fetchUtils.js";

const UPDATE_INTERVAL = 60 * 1000;

function MapManager() {
  const [gameState, setGameState] = React.useState(null);
  const [maps, setMaps] = React.useState([]);
  const statusIntervalRef = React.useRef(null);

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
    <Outlet context={{ maps }} />
  );
}

export default MapManager;
