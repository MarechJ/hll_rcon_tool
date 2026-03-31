import { cmd } from "@/utils/fetchUtils"

export const loader = async () => {
    const votemapStatus = await cmd.GET_VOTEMAP_STATUS()
    const votemapResults = await cmd.GET_VOTEMAP_RESULTS()
    return { votemapStatus, votemapResults }
}