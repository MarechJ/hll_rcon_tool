import { useQuery } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";

export const useTemplates = (key) => {
  const {
    data: templates,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["crcon", "templates", key], // Query key
    queryFn: async () =>
      cmd.GET_MESSAGE_TEMPLATES({ params: { category: key.toUpperCase() } }),
    initialData: [],
  });

  return templates;
};
