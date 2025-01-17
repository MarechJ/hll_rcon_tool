import React from "react";

import {Popover, PopoverContent, PopoverTrigger,} from "@/components/ui/popover";
import {List} from "lucide-react";
import {useTranslation} from "react-i18next";
import {Table} from "@tanstack/react-table";
import {Player} from "@/types/player";
import {Checkbox} from "@/components/ui/checkbox";
import {ColumnCategory} from "@/lib/tables";

interface ColumnMenuProps<TData> {
  table: Table<TData>
}

export function ColumnMenu<TData extends Player>({ table }: ColumnMenuProps<TData>) {
  const { t } = useTranslation('game');

  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger className={'rounded-md border border-input bg-background px-3 py-2 hover:bg-accent'}>
        <List size={20} />
      </PopoverTrigger>
      <PopoverContent
        align="start"
        className="w-full"
      >
        <div className="p2 flex flex-wrap flex-row gap-2 max-w-[100vw]">
          {Object.values(ColumnCategory).map(category =>
            <div className="divide-y-2">
              <div className="px-2">
                {t(`playersTable.${category}`)}
              </div>
              <div className="py-2">
                {table
                  .getAllColumns()
                  .filter(col => col.getCanHide())
                  .filter(col => col.columnDef.meta?.category === category)
                  .map((column) => (
                    <div
                      key={column.id}
                      onClick={column.getToggleVisibilityHandler()}
                      className="px-2 flex items-center cursor-pointer select-none hover:bg-accent"
                    >
                      <Checkbox checked={column.getIsVisible()} disabled={!column.getCanHide()} />
                      <span className="pl-3">{column.columnDef.meta?.label}</span>
                    </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
};
