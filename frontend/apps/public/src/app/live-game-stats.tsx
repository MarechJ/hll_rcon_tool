"use client"

import { useLiveGameStatsQuery } from "../utils/queries/live-game-stats";
import GameStats from "../components/game/game-stats";

export default function LiveGameStats() {
    const [liveGameStats] = useLiveGameStatsQuery();

    return <GameStats stats={liveGameStats.stats} />
}