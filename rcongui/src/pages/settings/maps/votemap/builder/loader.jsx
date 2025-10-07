import { cmd } from "@/utils/fetchUtils"

export const loader = async () => {
    const whitelist = await cmd.GET_VOTEMAP_WHITELIST()
    return { whitelist }
}