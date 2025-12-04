import { cmd } from "@/utils/fetchUtils"

export const loader = async () => {
    const serverName = await cmd.GET_SERVER_NAME()
    const serverNameConfig = await cmd.GET_SERVER_NAME_CHANGE_CONFIG()
    return { serverName, serverNameConfig }
}