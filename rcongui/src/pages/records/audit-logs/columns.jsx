import dayjs from "dayjs";

export const auditLogsColumns = [
  {
    header: "Time",
    accessorKey: "creation_time",
    cell: ({ row }) => {
      return dayjs(row.original.creation_time).format("lll");
    },
  },
  {
    header: "User",
    accessorKey: "username",
    width: 120,
  },
  {
    header: "Action",
    accessorKey: "command",
    width: 120,
  },
];
