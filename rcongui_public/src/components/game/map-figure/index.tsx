import { cn } from '@/lib/utils'
import React from 'react'

type MapFigureProps = {
  src: string
  name: string
  text?: string
  muted?: boolean
} & React.ComponentProps<'figure'>

export default function MapFigure({ src, name, text, muted, ...props }: MapFigureProps) {
  return (
    <figure className={cn('relative min-h-12', props.className)}>
      <img src={src} alt="" className={cn('w-full h-full object-cover', muted ? 'grayscale-[50]' : '')} />
      <figcaption className="absolute bottom-0 min-h-12 w-full p-1 text-center text-sm font-bold bg-background/75 group-hover:bg-background/60">
        {text && <div className="text-xs">{text}</div>}
        <div>{name}</div>
      </figcaption>
    </figure>
  )
}
