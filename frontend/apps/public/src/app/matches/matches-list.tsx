'use client';

import { useGamesQuery } from "../../utils/queries/scoreboard-maps"
import { columns } from "./match-columns";
import { DataTable as MatchTable } from "./match-table";

export default function MatchesList() {
    const [matches] = useGamesQuery()
    return (
        <div>
            <h1 className="text-2xl py-4">Last games</h1>
            <MatchTable data={matches.maps} columns={columns} />
        </div>
    )
}