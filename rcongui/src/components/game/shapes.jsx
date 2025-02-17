import { LockOutlined } from '@mui/icons-material'
import { Box, styled } from '@mui/material'

const romanDigits = ['I', 'II', 'III', 'IV', 'V']

// Base shape styles for both components
const shapeStyles = {
  flex: '0 0 20%',
  width: '20%',
  textAlign: 'center',
  display: 'grid',
  placeItems: 'center',
}

// Styled component for the neutral rectangle
const NeutralBox = styled(Box)({
  ...shapeStyles,
  backgroundColor: '#e5e5e5', // neutral-200 equivalent
  clipPath: 'polygon(0% 0%, 100% 0, 95% 50%, 100% 100%, 0% 100%, 5% 50%)',
})

export function RectangleNeutral() {
  return <NeutralBox />
}

export function Arrow({ team, highlighted, mode, order, direction, ...props }) {
  return (
    <Box
      sx={{
        ...shapeStyles,
        clipPath:
          direction === 'right'
            ? 'polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%, 5% 50%)'
            : 'polygon(5% 0%, 100% 0, 95% 50%, 100% 100%, 5% 100%, 0% 50%)',
        borderTop: highlighted ? 'none' : '4px solid',
        borderColor: team === 'axis' ? '#ef4444' : '#3b82f6', // red-500 : blue-500
        backgroundColor: highlighted
          ? team === 'axis'
            ? '#ef4444'
            : '#3b82f6'
          : team === 'axis'
          ? '#fca5a5'
          : '#93c5fd', // red-300 : blue-300
        opacity: highlighted ? 1 : undefined,
      }}
      {...props}
    >
      {!highlighted && mode === 'warfare' && (
        <LockOutlined
          sx={{
            strokeWidth: {
              xs: 3,
              md: 4,
              lg: 5,
            },
            fontSize: {
              xs: '0.75rem',
              sm: '1rem',
              md: '1.25rem',
              lg: '1.5rem',
            },
          }}
        />
      )}
      {mode === 'offensive' && order !== undefined && <span>{romanDigits[order]}</span>}
    </Box>
  )
}

export const ArrowsContainer = styled(Box)({
  width: '100%',
  display: 'flex',
  flexDirection: 'row',
  paddingLeft: '16px',
  paddingRight: '16px',
  marginBottom: '8px',
  height: {
    xs: '1rem',
    md: '1.5rem',
    lg: '2rem',
  },
})

const MAX_SCORE = 5

export const OffensiveArrows = ({ score, map }) => (
  <>
    {Array(score.allies)
      .fill(null)
      .map((_, index) => (
        <Arrow
          key={`score-${index}`}
          direction={map.attackers === 'allies' ? 'right' : 'left'}
          team="allies"
          mode="offensive"
          order={index}
          highlighted={index === 4}
        />
      ))}
    {Array(score.axis)
      .fill(null)
      .map((_, index) => (
        <Arrow
          key={`score-${index}`}
          direction={map.attackers === 'allies' ? 'right' : 'left'}
          team="axis"
          mode="offensive"
          highlighted={index === 0}
          order={(score.allies ?? 0) + index}
        />
      ))}
  </>
)

export const WarfareArrows = ({ score }) => {
  const isGameFinished = score.allies === MAX_SCORE || score.axis === MAX_SCORE
  const isTied = score.allies === score.axis
  const shouldHighlight = !isTied && !isGameFinished

  return (
    <>
      {Array(score.allies)
        .fill(null)
        .map((_, index, arr) => (
          <Arrow
            key={`score-${index}`}
            direction="right"
            team="allies"
            mode="warfare"
            highlighted={index === arr.length - 1 && shouldHighlight}
          />
        ))}
      {isTied && <RectangleNeutral />}
      {Array(score.axis)
        .fill(null)
        .map((_, index) => (
          <Arrow
            key={`score-${index}`}
            direction="left"
            team="axis"
            mode="warfare"
            highlighted={index === 0 && shouldHighlight}
          />
        ))}
    </>
  )
}
