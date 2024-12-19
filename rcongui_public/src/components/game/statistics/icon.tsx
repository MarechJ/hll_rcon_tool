export function IconStatistic({ text, stat, children }: { text: string; stat: number; children: React.ReactNode }) {
  return (
    <div className='flex flex-col justify-center items-center divide-y divide-foreground gap-1 p-2'>
      <div className='flex flex-col items-center justify-center space-y'>
        <span className='p-1 lg:p-2 rounded-md'>{children}</span>
        <span className='text-xs'>{text}</span>
      </div>
      <span className='w-10 text-center font-semibold'>{stat}</span>
    </div>
  )
}
