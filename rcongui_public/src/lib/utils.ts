import {type ClassValue, clsx} from 'clsx'
import {twMerge} from 'tailwind-merge'
import dayjs from 'dayjs';
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const downloadCSV = (data: string, filename: string) => {
  const bytes = new TextEncoder().encode(data)
  const blob = new Blob([bytes], {
    type: 'application/csv;charset=utf-8',
  })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.style.display = 'none'
  a.href = url
  a.download = `${filename}.csv`
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  a.remove()
}

export const dayjsLocal = (date: string) => {
  const tz = dayjs.tz.guess();
  return dayjs.utc(date).tz(tz);
};
