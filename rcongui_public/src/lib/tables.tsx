import {RowData} from "@tanstack/react-table";

declare module '@tanstack/react-table' {
  interface ColumnMeta<TData extends RowData, TValue> {
    label: string
    category: ColumnCategory
  }
}

export enum ColumnCategory {
  GENERAL = 'general',
  ADVANCED = 'advanced',
  INGAME = 'ingame',
}
