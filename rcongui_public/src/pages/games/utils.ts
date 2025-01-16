import dayjs from 'dayjs'

export function getGameDuration(start: string, end: string) {
  const duration = dayjs.duration(dayjs(end).diff(dayjs(start)));

  return duration.format('H:mm:ss');
}
