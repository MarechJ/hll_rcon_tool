import { cmd } from "@/utils/fetchUtils"

export const loader = async () => {
    const shuffleEnabled = await cmd.GET_MAP_ROTATION_SHUFFLE()
    return { shuffleEnabled }
}