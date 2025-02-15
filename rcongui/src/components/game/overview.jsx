import { Box, Typography, styled } from '@mui/material'
import { ArrowsContainer, OffensiveArrows, WarfareArrows } from './shapes'

// sx={{ display: 'flex', justifyContent: 'start', width: { xs: 24, sm: 32, lg: 40 }, height: { xs: 24, sm: 32, lg: 40 } }}
const TeamImageWrapper = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'start',
  width: 40,
  height: 40,
//   [theme.breakpoints.up('sm')]: {
//     width: 32,
//     height: 32,
//   },
}))
const TeamImage = styled('img')(({ theme }) => ({
  width: 40,
  height: 40,
//   [theme.breakpoints.up('sm')]: {
//     width: 32,
//     height: 32,
//   },
//   [theme.breakpoints.up('md')]: {
//     width: 40,
//     height: 40,
//   },
  maxWidth: 'none',
}))

const TeamDivider = styled(Box)(({ team, theme }) => ({
  flexGrow: 1,
  alignSelf: 'center',
  borderBottom: '6px double',
  borderColor: team === 'allies' ? '#3b82f6' : '#ef4444', // blue-500 : red-500
  margin: '0 4px',
  [theme.breakpoints.down('sm')]: {
    display: 'none',
  },
}))

const MobileTeamDivider = styled(Box)(({ team, theme }) => ({
  width: '100%',
  alignSelf: 'center',
  borderTop: '6px double',
  borderColor: team === 'allies' ? '#3b82f6' : '#ef4444',
  margin: '0 4px',
  [theme.breakpoints.up('sm')]: {
    display: 'none',
  },
}))

export default function GameOverview({
  map,
  time,
  allies,
  axis,
  mode,
  mapName,
  axisCount,
  alliesCount,
  score,
}) {

  const displayArrows = () => {
    if (score.allies === undefined || score.axis === undefined) return null

    return (
      <ArrowsContainer>
        {mode === 'offensive' && <OffensiveArrows score={score} map={map} />}
        {mode === 'warfare' && <WarfareArrows score={score} />}
      </ArrowsContainer>
    )
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%', pt: 1 }}>
      {displayArrows()}
      <Typography variant="body2" textAlign="center">
        {time}
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center', px: { lg: 2 } }}>
        <Box sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', flexBasis: '100%' }}>
          <TeamImageWrapper>
            <TeamImage src={`/icons/teams/${allies.name}.webp`} alt={allies.team} />
          </TeamImageWrapper>
          <Box sx={{ display: 'flex', flexDirection: 'column', textAlign: 'right', flexGrow: 1 }}>
            <Typography variant="h6" sx={{ fontSize: { lg: '1rem' }, fontWeight: 'bold', textTransform: 'uppercase' }}>
              {allies.team}
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'row', fontSize: '0.875rem' }}>
              <TeamDivider team="allies" />
              {alliesCount !== undefined && (
                <Box sx={{ flexGrow: { xs: 1, sm: 0 } }}>
                  {alliesCount}
                </Box>
              )}
            </Box>
          </Box>
        </Box>

        <Typography
          variant="h3"
          sx={{
            flexBasis: '50%',
            minWidth: { xs: '6rem', lg: '10rem' },
            textAlign: 'center',
            fontSize: { xs: '1.25rem', lg: '2.75rem' },
          }}
        >
          {score.allies ?? '?'} : {score.axis ?? '?'}
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', flexBasis: '100%' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', textAlign: 'left', width: '100%' }}>
            <Typography variant="h6" sx={{ fontSize: { lg: '1rem' }, fontWeight: 'bold', textTransform: 'uppercase' }}>
              {axis.team}
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'row', fontSize: '0.875rem' }}>
              {axisCount !== undefined && (
                <Box>
                  {axisCount}
                </Box>
              )}
              <TeamDivider team="axis" />
            </Box>
          </Box>
          <TeamImageWrapper>
            <TeamImage src={`/icons/teams/${axis.name}.webp`} alt={axis.team} />
          </TeamImageWrapper>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', textAlign: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', flexDirection: 'row' }}>
          <MobileTeamDivider team="allies" />
          <Typography variant="body2" sx={{ minWidth: 'fit-content', flexGrow: 1 }}>
            {mapName}
          </Typography>
          <MobileTeamDivider team="axis" />
        </Box>
        <Typography variant="caption" sx={{ textTransform: 'capitalize' }}>
          {mode}
          {map.attackers && ` - ${map.attackers}`}
        </Typography>
      </Box>
    </Box>
  )
}
