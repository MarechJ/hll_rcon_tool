import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { gameQueryOptions } from "@/queries/game-query";
import dayjs from "dayjs";

const icons = {
  idle: "⚫",
  empty: "🟡",
  loading: "🟠",
  error: "🔴",
  normal: "🟢",
  ending: "🏁",
};

const numberOfBlinks = 3;
const blinkInterval = 500;

const TitleManager = () => {
  const {
    data: status,
    isLoading,
    isError,
  } = useQuery({
    ...gameQueryOptions.publicState(),
    refetchIntervalInBackground: true,
  });

  const [pendingTitleIcon, setPendingTitleIcon] = useState("");
  const [titleIcon, setTitleIcon] = useState(icons.loading);
  const [titleText, setTitleText] = useState("Loading...");
  const titleTimeoutRef = useRef(null);

  useEffect(() => {
    let text = "";
    let icon = icons.normal;

    if (isLoading) {
      text = "Loading...";
      icon = icons.loading;
    } else if (isError) {
      text = "Error loading server status";
      icon = icons.error;
    } else {
      const serverName = status.name.short_name;
      const numCurrentPlayers = status.player_count;
      const map = status.current_map.map;
      const mapName = map.pretty_name;

      if (status.time_remaining === 0) {
        icon = icons.idle;
      } else if (status.time_remaining <= 90) {
        // Not sure how to handle offensive mode
        // Lets just use a flag for now although it's not perfect
        icon = icons.ending;
      } else if (numCurrentPlayers === 0) {
        icon = icons.empty;
      }

      text = `${serverName} (${numCurrentPlayers}) | ${dayjs
        .duration(status.time_remaining, "seconds")
        .format("HH:mm:ss")} | ${mapName}`;
    }

    setTitleText(text);
    setPendingTitleIcon(icon);
  }, [status, isLoading, isError]);

  useEffect(() => {
    let counter = 0;
    const nextIcon = pendingTitleIcon;
    const currIcon = titleIcon;

    if (pendingTitleIcon && currIcon !== nextIcon) {
      titleTimeoutRef.current = setInterval(() => {
        counter++;
        if (counter % 2 === 1) {
          document.title = `${nextIcon} ${titleText}`;
        } else {
          document.title = `${currIcon} ${titleText}`;
        }
        if (counter === numberOfBlinks * 2) {
          counter = 0;
          setPendingTitleIcon("");
          setTitleIcon(nextIcon);
          clearInterval(titleTimeoutRef.current);
        }
      }, blinkInterval);
    } else {
      document.title = `${titleIcon} ${titleText}`;
    }

    return () => {
      titleTimeoutRef?.current && clearInterval(titleTimeoutRef.current);
    };
  }, [pendingTitleIcon, titleIcon, titleText, titleTimeoutRef]);
};

export default TitleManager;
