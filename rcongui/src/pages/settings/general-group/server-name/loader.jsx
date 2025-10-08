import { cmd } from "@/utils/fetchUtils"

export const loader = async () => {
    const rotation = await cmd.GET_MAP_ROTATION()
    return { rotation }
}