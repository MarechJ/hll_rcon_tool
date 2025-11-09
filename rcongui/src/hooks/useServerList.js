import { useQuery } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";

export function useServerList(options = {}) {
  return useQuery({
    queryKey: [{ queryIdentifier: "get_server_list" }],
    queryFn: cmd.GET_GAME_SERVER_LIST,
    select: (data) => {
      if (!data || !Array.isArray(data)) {
        return {
          allServers: [],
          currentServer: null,
          otherServers: [],
          serverMap: {},
        };
      }

      const currentServer = data.find(server => server.current === true) || null;
      const otherServers = data.filter(server => server.current !== true);
      
      const serverMap = data.reduce((acc, server) => {
        acc[server.server_number] = server.name;
        return acc;
      }, {});

      return {
        allServers: data,
        currentServer,
        otherServers,
        serverMap,
      };
    },
    ...options,
  });
}

