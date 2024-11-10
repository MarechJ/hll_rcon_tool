import { useReactTable } from "@tanstack/react-table";
import { GameListTable } from "./game-list-table";
import { columns } from "./game-list-columns";
import { cmd } from "@/utils/fetchUtils";
import { useLoaderData, useSearchParams } from "react-router-dom";
import {
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
} from "@tanstack/react-table";
import { gameQueryOptions } from "@/queries/game-query";
import { useQuery } from "@tanstack/react-query";

export const loader = async () => {
  return await cmd.GET_COMPLETED_GAMES();
};

const GamesPage = () => {
  const data = useLoaderData();

  const [searchParams] = useSearchParams();
  const page = Number(searchParams.get("page") ?? 1);
  const pageSize = Number(searchParams.get("page_size") ?? 50);
  const maxPages = Math.ceil(data.total / pageSize);

  const { data: games, isLoading } = useQuery({
    ...gameQueryOptions.list(page, pageSize),
    initialData: data,
  });

  const table = useReactTable({
    columns: columns,
    data: games?.maps ?? [],
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    filterFns: {
      mapFilter: (row, id, filterValue) => {
        return row.original.map.pretty_name
          .toLowerCase()
          .includes(filterValue.toLowerCase());
      },
    },
  });

  return (
    <div>
      <h1>Games</h1>
      <GameListTable table={table} page={page} maxPages={maxPages} />
    </div>
  );
};

export default GamesPage;
