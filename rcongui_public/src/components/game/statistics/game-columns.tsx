'use client'

import {Column, ColumnDef } from '@tanstack/react-table'
import {Player, PlayerTeamAssociation, PlayerWithStatus} from '@/types/player'
import {IconHeader as Header} from './column-header'
import {Status} from './player-status'
import {isPlayerWithStatus} from './player/utils'
import {Button} from '@/components/ui/button'
import {useTranslation} from 'react-i18next'
import {TeamIndicator} from '@/components/game/statistics/team-indicator'
import {WeaponTypeBar} from "@/components/game/statistics/weapon-type-bar";
import {getTeamFromAssociation} from "@/components/game/statistics/utils";
import {ScaleIcon} from "lucide-react";
import {Awards} from "@/components/game/statistics/award";
import {PlayerBaseWithAwards} from "@/pages/games/[id]";

const threeDigitsWidth = 40
const fourDigitsWidth = 50

function SortableHeader({ column, desc }: { column: Column<Player>; desc: string }) {
  return (
    <div className="text-right">
      <Button
        variant={'text'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() !== 'desc')
        }}
        className="px-0"
      >
        {desc}
      </Button>
    </div>
  )
}

function pointColumns(completed: boolean): ColumnDef<Player | PlayerWithStatus>[] {
  const { t } = useTranslation('game');

  return [
    ...completed ? [killCategoryColumn()] : [],
    {
      id: 'kills',
      meta: { label: t('playersTable.kills')},
      accessorKey: 'kills',
      size: threeDigitsWidth,
      header: function KillsHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/infantry.png'}
            desc={t('playersTable.kills')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    },
    {
      id: 'kill_death_ratio',
      meta: { label: t('score.k/d')},
      accessorKey: 'kill_death_ratio',
      size: fourDigitsWidth,
      header: function DeathsHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            icon={<ScaleIcon/>}
            desc={t('score.k/d')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
      cell: ({row}) => {
        const player = row.original;
        return <div className={"text-right whitespace-pre"}>
          {player.kill_death_ratio.toFixed(1)}
        </div>;
      },
    },
    {
      id: 'deaths',
      meta: { label: t('playersTable.deaths')},
      accessorKey: 'deaths',
      size: fourDigitsWidth,
      header: function DeathsHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/medic.png'}
            desc={t('playersTable.deaths')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    },
    ...completed ? [deathCategoryColumn()] : [],
    {
      id: 'kills_per_minute',
      meta: { label: t('playersTable.killsPerMinute')},
      accessorKey: 'kills_per_minute',
      header: function KpmHeader({ column }) {
        const { t } = useTranslation('game')
        return <SortableHeader column={column} desc={t('playersTable.killsPerMinute')} />
      },
      size: 20,
    },
    {
      id: 'deaths_per_minute',
      meta: { label: t('playersTable.deathsPerMinute')},
      accessorKey: 'deaths_per_minute',
      header: function KpmHeader({ column }) {
        const { t } = useTranslation('game')
        return <SortableHeader column={column} desc={t('playersTable.deathsPerMinute')} />
      },
      size: 20,
    },
    {
      id: 'combat',
      meta: { label: t('playersTable.combat')},
      accessorKey: 'combat',
      size: fourDigitsWidth,
      header: function CombatHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/score_combat.png'}
            desc={t('playersTable.combat')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    },
    {
      id: 'offense',
      meta: { label: t('playersTable.offense')},
      accessorKey: 'offense',
      size: fourDigitsWidth,
      header: function OffenseHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/score_offensive.png'}
            desc={t('playersTable.offense')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    },
    {
      id: 'defense',
      meta: { label: t('playersTable.defense')},
      accessorKey: 'defense',
      size: fourDigitsWidth,
      header: function DefenseHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/score_defensive.png'}
            desc={t('playersTable.defense')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    },
    {
      id: 'support',
      meta: { label: t('playersTable.support')},
      accessorKey: 'support',
      size: fourDigitsWidth,
      header: function SupportHeader({ column }) {
        const { t } = useTranslation('game')
        return (
          <Header
            src={'/roles/score_support.png'}
            desc={t('playersTable.support')}
            className={"text-right"}
            onClick={() => {
              column.toggleSorting(column.getIsSorted() !== 'desc')
            }}
          />
        )
      },
    },
  ];
}

const playerColumn = (handlePlayerClick: (id: string) => void): ColumnDef<Player | PlayerWithStatus> => ({
  id: 'player',
  accessorKey: 'player',
  header: function NameHeader() {
    const { t } = useTranslation('game')
    return <div>{t('playersTable.player')}</div>
  },
  cell: ({ row }) => {
    const name = String(row.getValue('player'))
    const id = String(row.original.player_id)

    return (
      <div className="text-left">
        <Button
          variant={'text'}
          className="pl-0"
          onClick={() => {
            handlePlayerClick(id)
          }}
        >
          {name}
        </Button>
      </div>
    )
  },
  filterFn: (row, columnId: string, filterValue: string[]) => {
    if (filterValue === undefined || filterValue.length === 0) {
      return true
    }
    const value: string = row.getValue(columnId)
    return filterValue.some((v: string) => value.toLowerCase().includes(v.toLowerCase()))
  },
  enableHiding: false,
})

const awardColumn = (): ColumnDef<Player | PlayerBaseWithAwards | PlayerWithStatus>  => {
  const { t } = useTranslation('game');
  return {
    id: 'award',
    meta: {label: t('playersTable.awards')},
    header: function NameHeader() {
      const {t} = useTranslation('game')
      return <div className="text-right">{t('playersTable.awards')}</div>
    },
    cell: ({row}) => {
      return 'awards' in row.original ? <Awards player={row.original}/> : null
    },
    size: 20,
  }
};

const teamColumn = (): ColumnDef<Player | PlayerWithStatus> => {
  const { t } = useTranslation('game');

  return {
    id: 'team',
    meta: { label: t('playersTable.team')},
    accessorKey: 'team',
    header: function TeamHeader() {
      const {t} = useTranslation('game')
      return <div className={"text-center"}>{t('playersTable.team')}</div>
    },
    size: 20,
    filterFn: (row, columnId, filterValue) => {
      if (!filterValue || filterValue === 'all') {
        return true
      }
      const cellValue: PlayerTeamAssociation = row.getValue(columnId);
      return getTeamFromAssociation(cellValue) === filterValue;
    },
    cell: ({row}) => {
      const player = row.original;
      return <div className={"text-center"}>
        <TeamIndicator team={getTeamFromAssociation(player.team)} className="inline-block"/>
      </div>;
    },
  };
}

const killCategoryColumn = (): ColumnDef<Player | PlayerWithStatus> => {
  const { t } = useTranslation('game');

  return {
    id: 'kills_by_category',
    meta: { label: t('playersTable.killsByCategory')},
    accessorKey: 'kills_by_category',
    header: function KillCategoryHeader() {
      const {t} = useTranslation('game')
      return <div>{t('playersTable.killsByCategory')}</div>
    },
    size: 100,
    cell: ({row}) => {
      const player = row.original;
      return <WeaponTypeBar totalKills={player.kills} killsByType={player.kills_by_type}/>;
    },
  }
};

const deathCategoryColumn = (): ColumnDef<Player | PlayerWithStatus> => {
  const { t } = useTranslation('game');

  return {
    id: 'deaths_by_category',
    meta: { label: t('playersTable.deathsByCategory')},
    accessorKey: 'deaths_by_category',
    header: function DeathCategoryHeader() {
      const {t} = useTranslation('game')
      return <div>{t('playersTable.deathsByCategory')}</div>
    },
    size: 100,
    cell: ({row}) => {
      const player = row.original;
      return <WeaponTypeBar totalKills={player.deaths} killsByType={player.deaths_by_type}/>;
    },
  }
};

const statusColumn: ColumnDef<Player | PlayerWithStatus> = {
  id: 'is_online',
  accessorKey: 'is_online',
  header: function StatusHeader() {
    const { t } = useTranslation('game')
    return <div className="sr-only w-4">{t('playersTable.status')}</div>
  },
  size: 20,
  filterFn: (row, columnId, filterValue) => {
    if (!filterValue || filterValue === 'all') {
      return true
    }
    const cellValue = row.getValue(columnId) ? 'online' : 'offline'
    return cellValue === filterValue
  },
  cell: ({ row }) => {
    const player = row.original
    return isPlayerWithStatus(player) ? <Status player={player} className="block" /> : null
  },
  enableHiding: false,
}

export const getLiveGameColumns = (handlePlayerClick: (id: string) => void): ColumnDef<Player | PlayerWithStatus>[] => [
  statusColumn,
  playerColumn(handlePlayerClick),
  ...pointColumns(false),
]

export const getCompletedGameColumns = (
  handlePlayerClick: (id: string) => void,
): ColumnDef<Player | PlayerWithStatus | PlayerBaseWithAwards>[] => [teamColumn(), playerColumn(handlePlayerClick), awardColumn(), ...pointColumns(true)]
