export function downloadGame(player_stats) {
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
      'Death by Weapons'
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
      JSON.stringify(p.death_by_weapons)
    ])
  ]
    .map((l) => '"' + l.map((co) => (typeof co === 'string' ? co.replaceAll('"', '""') : co)).join('","') + '"')
    .join('\n')

  const bytes = new TextEncoder().encode(data)
  const blob = new Blob([bytes], {
    type: 'application/csv;charset=utf-8'
  })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.style.display = 'none'
  a.href = url
  a.download = 'tableDownload.csv'
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  a.remove()
}
