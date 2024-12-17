import { useEffect, useState } from "react";
import { SearchInput } from "@/components/shared/SearchInput";

export const DebouncedSearchInput = ({
  initialValue = "",
  onChange,
  debounce = 500,
  ...props
}) => {
  const [search, setSearch] = useState(initialValue);

  useEffect(() => {
    setSearch(initialValue);
  }, [initialValue]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      onChange(search);
    }, debounce);

    return () => clearTimeout(timeout);
  }, [search]);

  return (
    <SearchInput
      value={search}
      onClear={(e) => setSearch("")}
      onChange={(e) => setSearch(e.target.value)}
      {...props}
    />
  );
};
