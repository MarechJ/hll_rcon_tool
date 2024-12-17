import dayjs from 'dayjs'
import LocalizedFormat from 'dayjs/plugin/localizedFormat'
import { Link } from 'react-router-dom'
import { Box, Button, Typography } from '@mui/material'
import { getGameDuration } from '@/utils/lib'
import { SortableHeader } from '@/components/table/styles'

dayjs.extend(LocalizedFormat)

export const gameIdColumn = {
  accessorKey: 'id',
  header: 'ID',
  cell: ({ cell }) => {
    const matchId = cell.getValue()
    return (
      <Button component={Link} to={`/stats/games/${matchId}`} variant='text'>
        {matchId}
      </Button>
    )
  },
  meta: {
    variant: 'short'
  }
}

export const mapColumn = {
  header: SortableHeader('Map'),
  id: 'map',
  accessorKey: 'map',
  minSize: 200,
  size: 200,
  filterFn: 'mapFilter',
  cell: ({ cell }) => {
    const matchMap = cell.getValue()
    const size = 60
    const ratio = 9 / 16
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'row',
          gap: 0.5,
          width: 'max-content'
        }}
      >
        <img src={'/maps/icons/' + matchMap.image_name} width={size} height={size * ratio} alt='' />
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          <Typography variant='body1' sx={{ fontWeight: 600, lineHeight: 1 }}>
            {matchMap.map.pretty_name}
          </Typography>
          <Typography variant='subtitle2' sx={{ display: 'flex', flexDirection: 'row', fontWeight: 400 }}>
            <Box component='span' sx={{ paddingRight: 0.5 }}>
              {matchMap.game_mode[0].toUpperCase() + matchMap.game_mode.slice(1)}
            </Box>
            <Box component='span'>{matchMap.environment}</Box>
          </Typography>
        </Box>
      </Box>
    )
  },
  meta: {
    variant: 'content'
  }
}

export const resultColumn = {
  header: 'Result',
  id: 'result',
  accessorFn: (row) => `${row.result?.allied ?? '?'} - ${row.result?.axis ?? '?'}`,
  meta: {
    variant: 'short'
  }
}

export const startColumn = {
  header: SortableHeader('Start'),
  accessorKey: 'start',
  cell: ({ cell }) => dayjs(cell.getValue()).format('L LT'),
  meta: {
    variant: 'name'
  }
}

export const durationColumn = {
  header: SortableHeader('Duration'),
  accessorKey: 'duration',
  cell: ({ row }) => getGameDuration(row.original.start, row.original.end)
}

export const columns = [gameIdColumn, mapColumn, resultColumn, startColumn, durationColumn]
