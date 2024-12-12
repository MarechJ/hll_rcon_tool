import { LockIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

const romanDigits = ['I', 'II', 'III', 'IV', 'V']

export function RectangleNeutral() {
  return (
    <div
      className={cn(
        'text-center basis-1/5 w-1/5 bg-neutral-200 [clip-path:polygon(0%_0%,100%_0,95%_50%,100%_100%,0%_100%,5%_50%)]',
      )}
    ></div>
  )
}

export function Arrow({
  team,
  highlighted,
  mode,
  order,
  direction,
}: {
  team?: 'axis' | 'allies'
  mode?: 'warfare' | 'offensive' | 'skirmish'
  highlighted?: boolean
  order?: number
  direction: 'left' | 'right'
}) {
  return (
    <div
      className={cn(
        'grid items-center justify-center text-center basis-1/5 w-1/5 border-t-4',
        direction === 'right' && '[clip-path:polygon(0%_0%,95%_0%,100%_50%,95%_100%,0%_100%,5%_50%)]',
        direction === 'left' && '[clip-path:polygon(5%_0%,100%_0,95%_50%,100%_100%,5%_100%,0%_50%)]',
        team === 'axis' && 'bg-red-300 border-red-500',
        team === 'allies' && 'bg-blue-300 border-blue-500',
        highlighted && 'opacity-100 border-t-0',
        highlighted && team === 'axis' && 'bg-red-500',
        highlighted && team === 'allies' && 'bg-blue-500',
      )}
    >
      {!highlighted && mode === 'warfare' && (
        <LockIcon className="stroke-[3] size-2 md:stroke-[4] md:size-3 lg:size-4 lg:stroke-[5]" />
      )}
      {mode === 'offensive' && order !== undefined && <span>{romanDigits[order]}</span>}
    </div>
  )
}
