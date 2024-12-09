import { usePublicInfo } from '@/lib/queries/public-info'
import dayjs from 'dayjs'
import { Helmet } from 'react-helmet'
import duration from 'dayjs/plugin/duration'
import { useTranslation } from 'react-i18next'
import { Skeleton } from '@/components/ui/skeleton'
import LiveGameInfo from './live-game-info'
import LiveGameStats from './live-game-stats'
import { Spinner } from '@/components/spinner'

dayjs.extend(duration)

export default function Home() {
  const { t } = useTranslation('navigation')
  const { t: tNotFound } = useTranslation('notfound')
  const [game, { isLoading, isError }] = usePublicInfo()

  if (isError) {
    throw new Error(tNotFound('connectionError'))
  }

  return (
    <>
      <Helmet>
        <title>{t('currentGame')}</title>
      </Helmet>
      {isError ? (
        <div className="grid place-items-center w-full h-[200px]">
          <p className="text-red-500">{tNotFound('connectionError')}</p>
        </div>
      ) : isLoading || !game ? (
        <div className="grid place-items-center w-full h-[200px]">
          <Spinner />
        </div>
      ) : (
        <>
          <LiveGameInfo game={game} />
          <LiveGameStats />
        </>
      )}
    </>
  )
}
