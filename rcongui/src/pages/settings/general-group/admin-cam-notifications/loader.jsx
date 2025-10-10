import { cmd } from "@/utils/fetchUtils"

export const loader = async () => {
    const cameraConfig = await cmd.GET_CAMERA_NOTIFICATION_CONFIG()
    return { cameraConfig }
}