import { useReactTable } from "@tanstack/react-table";
import { GameListTable } from "./game-list-table";
import { columns } from "./game-list-columns";
import { cmd } from "@/utils/fetchUtils";
import { useLoaderData } from "react-router-dom";
import {
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
} from "@tanstack/react-table";

export const loader = async () => {
  return await cmd.GET_COMPLETED_GAMES();
};

const GamesPage = () => {
  const data = useLoaderData();
  const table = useReactTable({
    columns: columns,
    data: data.maps,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    filterFns: {
      mapFilter: (row, id, filterValue) => {
        return row.original.map.pretty_name
          .toLowerCase()
          .includes(filterValue.toLowerCase());
      },
    },
    initialState: {
      pagination: {
        pageIndex: 0,
        pageSize: 50,
      },
    },
  });

  return (
    <div>
      <h1>Games</h1>
      <GameListTable table={table} />
    </div>
  );
};

export default GamesPage;
