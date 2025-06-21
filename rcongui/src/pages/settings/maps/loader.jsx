import { cmd } from "@/utils/fetchUtils"

export const loader = async () => {
    const maps = await cmd.GET_MAPS()
    return { maps }    
}