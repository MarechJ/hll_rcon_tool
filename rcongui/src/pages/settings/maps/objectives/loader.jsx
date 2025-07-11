import { cmd } from "@/utils/fetchUtils"

export const loader = async () => {
    const objectives = await cmd.GET_MAP_OBJECTIVES()
    const gameState = await cmd.GET_GAME_STATE()
    return { objectives, gameState }
}