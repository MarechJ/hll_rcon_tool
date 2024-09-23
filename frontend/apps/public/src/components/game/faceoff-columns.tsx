"use client";

import { ColumnDef } from "@tanstack/react-table";
import clsx from "clsx";
import { Faceoff } from "./types";
import { Header } from "./column-header";

const nColSize = 40

export const columns: ColumnDef<Faceoff>[] = [
  {
    accessorKey: "name",
    header: 'Encounters',
  },
  {
    accessorKey: "kills",
    header: ({ column }) => (
      <Header
        header={"K"}
        desc={"Kills"}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === "asc");
        }}
      />
    ),
    cell: ({ cell }) => <div className='text-right px-1'>{String(cell.getValue())}</div>,
    size: nColSize,
  },
  {
    accessorKey: "deaths",
    header: ({ column }) => (
      <Header
        header={"D"}
        desc={"Deaths"}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === "asc");
        }}
      />
    ),
    cell: ({ cell }) => <div className='text-right px-1'>{String(cell.getValue())}</div>,
    size: nColSize,
  },
  {
    
    accessorKey: "diff",
    header: ({ column }) => (
      <Header
        header={"+/-"}
        desc={"Difference"}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === "asc");
        }}
      />
    ),
    size: nColSize,
    cell: ({ cell }) => {
        const diff = Number(cell.getValue());
        const textColor = diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : '';
        return <div className={clsx(textColor, 'text-right px-1')}>{diff}</div>
    }
  }
];