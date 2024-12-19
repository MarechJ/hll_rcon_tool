import { Box, Checkbox, Stack, styled, Tooltip, Typography } from '@mui/material'
import { Star, Warning } from '@mui/icons-material'
import { yellow } from '@mui/material/colors'
import dayjs from 'dayjs'
import { ActionMenuButton } from '@/features/player-action/ActionMenu'
import { generatePlayerActions } from '@/features/player-action/actions'
import { CountryFlag } from '@/components/shared/CountryFlag'
import { getPlayerTier, hasRecentWarnings, teamToNation, tierColors } from '@/utils/lib'
import { SortableHeader } from '@/components/table/styles'
import RemoveRedEyeIcon from '@mui/icons-material/RemoveRedEye'

export const Square = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'start',
  justifyContent: 'center',
  width: 16,
  height: 16,
  lineHeight: '16px',
  fontWeight: 'bold',
  backgroundColor: theme.palette.background.paper
}))

const LevelColored = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'level'
})((styledProps) => {
  const level = styledProps.level
  if (!level) return {}
  const tier = getPlayerTier(level)
  const color = tierColors[tier]
  return {
    color
  }
})

const Center = styled(Box)(() => ({
  display: 'grid',
  justifyItems: 'center',
  alignContent: 'center'
}))

export const columns = [
  {
    id: 'select',
    header: ({ table }) => (
      <Checkbox
        checked={table.getIsAllRowsSelected()}
        indeterminate={table.getIsSomePageRowsSelected()}
        onChange={table.getToggleAllRowsSelectedHandler()}
        size='small'
        sx={{
          p: 0
        }}
      />
    ),
    cell: ({ row }) => (
      <div>
        <Checkbox
          checked={row.getIsSelected()}
          disabled={!row.getCanSelect()}
          indeterminate={row.getIsSomeSelected()}
          onChange={row.getToggleSelectedHandler()}
          size='small'
          sx={{
            p: 0
          }}
        />
      </div>
    ),
    meta: {
      variant: 'icon'
    }
  },
  {
    accessorKey: 'team',
    id: 'team',
    header: SortableHeader('T'),
    cell: ({ row }) => {
      return (
        <Center>
          <Square>
            <img src={`/icons/teams/${teamToNation(row.original.team)}.webp`} width={16} height={16} />
          </Square>
        </Center>
      )
    },
    meta: {
      variant: 'icon'
    }
  },
  {
    id: 'unit',
    header: SortableHeader('U'),
    accessorKey: 'unit_name',
    // Group by unit name and team
    // getGroupingValue: (row) => `${row.original.unit_name ?? "-"}-${row.original.team}`,
    cell: ({ row }) => {
      return (
        <Center>
          <Square>{row.original.unit_name?.charAt(0)?.toUpperCase() ?? '-'}</Square>
        </Center>
      )
    },
    meta: {
      variant: 'icon'
    }
  },
  {
    id: 'role',
    header: SortableHeader('R'),
    accessorKey: 'role',
    cell: ({ row }) => {
      return (
        <Center>
          <Square
            sx={{
              bgcolor: (theme) => (theme.palette.mode === 'dark' ? 'background.paper' : '#121212')
            }}
          >
            <img src={`/icons/roles/${row.original.role}.png`} width={16} height={16} />
          </Square>
        </Center>
      )
    },
    meta: {
      variant: 'icon'
    }
  },
  {
    id: 'level',
    header: SortableHeader('LVL'),
    accessorKey: 'level',
    aggregationFn: 'mean',
    cell: ({ row }) => {
      return <LevelColored level={row.original.level}>{row.original.level}</LevelColored>
    },
    meta: {
      variant: 'short'
    }
  },
  {
    id: 'actions',
    header: '🛠️',
    accessorKey: 'actions',
    cell: ({ row }) => {
      return (
        <ActionMenuButton
          actions={generatePlayerActions({
            multiAction: false,
            onlineAction: true
          })}
          recipients={row.original}
          orientation='horizontal'
          disableRipple={true}
          sx={{
            width: 12,
            height: 12
          }}
        />
      )
    },
    meta: {
      variant: 'icon'
    }
  },
  {
    id: 'name',
    header: SortableHeader('Name'),
    accessorKey: 'name',
    cell: ({ row }) => {
      return (
        <Box
          sx={{
            textOverflow: 'ellipsis',
            overflow: 'hidden',
            textWrap: 'nowrap',
            width: '20ch'
          }}
        >
          <span>{row.original.name}</span>
        </Box>
      )
    }
  },
  {
    id: 'warnings',
    header: SortableHeader('⚠️'),
    accessorKey: 'profile.received_actions',
    cell: ({ row }) => {
      return hasRecentWarnings(row.original.profile.received_actions) ? (
        <Warning sx={{ fontSize: 12, color: yellow['500'] }} />
      ) : null
    },
    meta: {
      variant: 'icon'
    }
  },
  {
    id: 'watchlist',
    header: SortableHeader('👁️'),
    accessorKey: 'profile.watchlist',
    cell: ({ row }) => {
      return row.original.profile?.watchlist && row.original.profile?.watchlist?.is_watched ? (
        <RemoveRedEyeIcon sx={{ fontSize: 12 }} />
      ) : null
    },
    meta: {
      variant: 'icon'
    }
  },
  {
    id: 'country',
    header: SortableHeader('🌎'),
    accessorKey: 'country',
    cell: ({ row }) => {
      return row.original.country && row.original.country !== 'private' ? (
        <CountryFlag country={row.original.country} />
      ) : null
    },
    meta: {
      variant: 'icon'
    }
  },
  {
    id: 'vip',
    header: SortableHeader('VIP'),
    accessorKey: 'is_vip',
    cell: ({ row }) => {
      return row.original.is_vip ? <Star sx={{ fontSize: 12, color: yellow['500'] }} /> : null
    },
    meta: {
      variant: 'icon'
    }
  },
  {
    id: 'flags',
    header: 'Flags',
    accessorKey: 'profile.flags',
    cell: ({ row }) => {
      const flags = row.original.profile.flags
      if (!flags || flags.length === 0) return null
      const flagsCount = 2
      return (
        <Stack spacing={0.25} direction={'row'} alignItems={'center'}>
          {flags.slice(0, flagsCount).map(({ flag, comment: note, modified }) => (
            <Tooltip title={note} key={modified}>
              <Box>{flag}</Box>
            </Tooltip>
          ))}
          {flags.length - flagsCount > 0 ? (
            <Typography variant='caption' sx={{ fontSize: 12, pr: 0.5 }}>{`+${flags.length - flagsCount}`}</Typography>
          ) : null}
        </Stack>
      )
    }
  },
  {
    id: 'time',
    header: SortableHeader('Time'),
    accessorKey: 'profile.current_playtime_seconds',
    aggregationFn: 'mean',
    cell: ({ row }) => {
      return <>{dayjs.duration(row.original.profile.current_playtime_seconds, 'seconds').format('H:mm')}</>
    },
    meta: {
      variant: 'short'
    }
  }
]
