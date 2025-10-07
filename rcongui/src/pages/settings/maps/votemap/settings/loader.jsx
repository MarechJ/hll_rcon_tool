import { cmd } from "@/utils/fetchUtils"

export const loader = async () => {
    const config = await cmd.GET_VOTEMAP_CONFIG()
    return { config }
}