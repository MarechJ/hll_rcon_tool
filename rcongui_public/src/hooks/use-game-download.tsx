import { usePublicInfo } from '@/lib/queries/public-info'
import { downloadCSV } from '@/lib/utils'
import { Player } from '@/types/player'

export default function useGameDownload() {
  const [publicInfo] = usePublicInfo()

  const download = (player_stats: Player[], filename: string) => {
    const serverName = publicInfo?.name.short_name || publicInfo?.name.name.slice(0, 15) || ''
    const data = prepareData(player_stats)
    downloadCSV(data, filename + `_${serverName}`)
  }

  return { download }
}

function prepareData(player_stats: Player[]) {
  const data = [
    [
      'Player ID',
      'Name',
      'Kills',
      'Deaths',
      'K/D',
      'Max kill streak',
      'Kill(s) / minute',
      'Death(s) / minute',
      'Max death streak',
      'Max TK streak',
      'Death by TK',
      'Death by TK Streak',
      '(aprox.) Longest life min.',
      '(aprox.) Shortest life secs.',
      'Nemesis',
      'Victim',
      'Combat Effectiveness',
      'Support Points',
      'Defensive Points',
      'Offensive Points',
      'Weapons',
      'Death by Weapons',
    ],
    ...player_stats.map((p) => [
      p.player_id,
      p.player,
      p.kills,
      p.deaths,
      p.kill_death_ratio,
      p.kills_streak,
      p.kills_per_minute,
      p.deaths_per_minute,
      p.deaths_without_kill_streak,
      p.teamkills_streak,
      p.deaths_by_tk,
      p.deaths_by_tk_streak,
      p.longest_life_secs,
      p.shortest_life_secs,
      JSON.stringify(p.death_by),
      JSON.stringify(p.most_killed),
      p.combat,
      p.support,
      p.defense,
      p.offense,
      JSON.stringify(p.weapons),
      JSON.stringify(p.death_by_weapons),
    ]),
  ]
    .map((l) => '"' + l.map((co) => (typeof co === 'string' ? co.replaceAll('"', '""') : co)).join('","') + '"')
    .join('\n')

  return data
}
