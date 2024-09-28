'use client';

import dayjs from "dayjs";
import { useGamesQuery } from "../../utils/queries/scoreboard-maps"
import { ScoreboardMap } from "../../utils/queries/types";
import { columns } from "./match-columns";
import { DataTable as MatchTable } from "./match-table";

function validMatch(match: ScoreboardMap) {
    const start = dayjs(match.start)
    const end = dayjs(match.end)
    const diffMinutes = end.diff(start, 'minutes');

    return (
        diffMinutes < 100 && diffMinutes > 9
    )
}

export default function MatchesList() {
    const [matches] = useGamesQuery()

    const filteredMatches = matches.maps.filter(validMatch)

    return (
        <div>
            <h1 className="text-2xl py-4">Last games</h1>
            <MatchTable data={filteredMatches} columns={columns} />
        </div>
    )
}