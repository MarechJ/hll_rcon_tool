import dayjs from 'dayjs'

export function getGameDuration(start: string, end: string) {
  const totalSeconds = dayjs(end).diff(dayjs(start), 'seconds')
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  // Format the result as hh:mm:ss
  const formattedTime = `${String(hours).padStart(1, '0')}:${String(minutes).padStart(
    2,
    '0',
  )}:${String(seconds).padStart(2, '0')}`

  return formattedTime
}
