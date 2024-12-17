import { Outlet } from "react-router-dom";
import { get, getGameState } from "@/utils/fetchUtils.js";
import {useEffect, useRef, useState} from "react";

const UPDATE_INTERVAL = 60 * 1000;

function MapManager() {
  const [maps, setMaps] = useState([]);
  const statusIntervalRef = useRef(null);

  const updateGameState = async () => {
    await getGameState();
  };

  const getMaps = async () => {
    const response = await get("get_maps");
    const data = await response.json();
    const mapLayers = data.result;
    if (mapLayers) {
      setMaps(mapLayers);
    }
  };

  useEffect(() => {
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
