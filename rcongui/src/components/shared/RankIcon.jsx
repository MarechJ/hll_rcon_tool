import { toSnakeCase } from '@/utils/lib'

export const RankIcon = ({ rank, ...props }) => (
  <img src={`/icons/ranks/${toSnakeCase(rank)}.webp`} width={16} height={16} alt={rank} {...props} />
)
