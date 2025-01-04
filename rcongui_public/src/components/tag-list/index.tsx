import {Badge} from "@/components/ui/badge";
import {XCircleIcon} from "lucide-react";
import {InputHTMLAttributes, useEffect, useState} from "react";

interface TagListProps {
  value: string[],
  onChange: (value: string[]) => void
  debounce?: number,
};

export default function TagList({
  value: initialValue,
  onChange,
}: TagListProps & Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange'>) {
  const [value, setValue] = useState(initialValue)

  useEffect(() => {
    setValue(initialValue)
  }, [initialValue])

  useEffect(() => {
    onChange(value);
  }, [value])

  return <div className={'flex gap-1 flex-wrap'}>
    {value.map((v) => <RemovableBadge key={v} value={v} onClick={() => {
      setValue((o) => o.filter((ov) => ov !== v));
    }}/>)}
  </div>
}

function RemovableBadge({value, onClick}: {value: string, onClick: () => void}) {
  return <Badge className={'gap-1.5'}>
    <div>{value}</div>
    <XCircleIcon size={16} onClick={onClick} className={'cursor-pointer'}/>
  </Badge>
}
