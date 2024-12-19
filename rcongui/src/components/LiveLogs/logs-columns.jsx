import dayjs from 'dayjs'
import { Action, TIME_FORMAT } from '@/components/LiveLogs/Log'

/*
 Log example: 
    {
        "version": 1,
        "timestamp_ms": 1729630418000,
        "event_time": "2024-10-22T20:53:38",
        "relative_time_ms": -1632.637,
        "raw": "[1.10 sec (1729630418)] DISCONNECTED HereCookie76152 (e520836e51d683d06f56e06e4cb74118)",
        "line_without_time": "DISCONNECTED HereCookie76152 (e520836e51d683d06f56e06e4cb74118)",
        "action": "DISCONNECTED",
        "player_name_1": "HereCookie76152",
        "player_id_1": "e520836e51d683d06f56e06e4cb74118",
        "player_name_2": null,
        "player_id_2": null,
        "weapon": null,
        "message": "HereCookie76152 (e520836e51d683d06f56e06e4cb74118)",
        "sub_content": null
    }

    or

    {
        "version": 1,
        "timestamp_ms": 1729629560000,
        "event_time": "2024-10-22T20:39:20",
        "relative_time_ms": -1363.4550000000002,
        "raw": "[1.00 sec (1729629560)] TEAM KILL: blanquartmael(Axis/76561199409157448) -> PeaceUndead(Axis/6d7e77a018bc9213cb1045ea67324367) with WALTHER P38",
        "line_without_time": "TEAM KILL: blanquartmael(Axis/76561199409157448) -> PeaceUndead(Axis/6d7e77a018bc9213cb1045ea67324367) with WALTHER P38",
        "action": "TEAM KILL",
        "player_name_1": "blanquartmael",
        "player_id_1": "76561199409157448",
        "player_name_2": "PeaceUndead",
        "player_id_2": "6d7e77a018bc9213cb1045ea67324367",
        "weapon": "WALTHER P38",
        "message": "blanquartmael(Axis/76561199409157448) -> PeaceUndead(Axis/6d7e77a018bc9213cb1045ea67324367) with WALTHER P38",
        "sub_content": null
    }
*/

const removePlayerIds = (message) => {
  // Combine both regex patterns into one
  return message.replace(/\((?:(?:Axis|Allies)\/)?(?:[0-9]{17}|[A-Z0-9]{16})\)/g, '')
}

// Column definitions for the log table
export const logColumns = [
  {
    header: 'Time',
    accessorKey: 'timestamp_ms',
    cell: ({ row }) => {
      return dayjs(row.original.timestamp_ms).format(TIME_FORMAT)
    }
  },
  {
    header: 'Action',
    accessorKey: 'action',
    cell: ({ row }) => {
      return <Action type={row.original.action}>{row.original.action}</Action>
    }
  },
  {
    header: 'Message',
    accessorKey: 'message',
    // full width
    size: '100%',
    cell: ({ row }) => {
      return removePlayerIds(row.original.message)
    }
  }
]
