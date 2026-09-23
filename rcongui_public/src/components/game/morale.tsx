import { useTranslation } from 'react-i18next'
import { PublicInfo } from '@/types/api'
import { cn } from '@/lib/utils'

export type MoraleState = Pick<PublicInfo, 'allied_morale' | 'axis_morale' | 'initial_morale'>

export function Morale({ morale }: { morale: MoraleState }) {
  const { t } = useTranslation('game')

  const initial = morale.initial_morale
  const teams = [
    { name: t('allies'), value: morale.allied_morale, color: 'border-blue-500', reverse: false },
    { name: t('axis'), value: morale.axis_morale, color: 'border-red-500', reverse: true },
  ]

  return (
    <section aria-label={t('morale')} className="mt-2 mb-4 px-6 lg:px-8">
      <div className="mb-1 text-center text-xs uppercase tracking-wider text-muted-foreground">{t('morale')}</div>
      <div className="grid grid-cols-2 gap-6 lg:gap-8">
        {teams.map(({ name, value, color, reverse }) => (
          <div key={name} className="min-w-0">
            <div className={cn('mb-1 flex flex-wrap items-baseline justify-between gap-x-2 text-xs tabular-nums', reverse && 'flex-row-reverse')}>
              <span className="uppercase text-muted-foreground">{name}</span>
              <span className="font-bold">
                {Number.isFinite(value) ? value : '—'}
                {Number.isFinite(initial) && initial > 0 && <span className="font-normal text-muted-foreground"> / {initial}</span>}
              </span>
            </div>
            {Number.isFinite(value) && Number.isFinite(initial) && initial > 0 && (
              <div
                role="meter"
                className="h-[6px] overflow-hidden bg-secondary"
                aria-valuemin={0}
                aria-valuemax={initial}
                aria-valuenow={Math.min(initial, Math.max(0, value))}
                aria-label={`${name}: ${t('morale')}`}
                aria-valuetext={`${value} / ${initial}`}
              >
                <div
                  className={cn('h-full border-t-[6px] border-double transition-[width] duration-500 motion-reduce:transition-none', color, reverse && 'ml-auto')}
                  style={{ width: `${Math.min(100, Math.max(0, value / initial * 100))}%` }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
