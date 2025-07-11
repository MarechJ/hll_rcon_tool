import { cmd } from "@/utils/fetchUtils"

export const loader = async () => {
    const mapListStatus = await cmd.GET_VOTEMAP_STATUS()
    const config = await cmd.GET_VOTEMAP_CONFIG()
    return { mapListStatus, config }
}