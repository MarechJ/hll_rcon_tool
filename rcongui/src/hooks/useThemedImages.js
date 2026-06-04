import { useTheme } from "@mui/material"

const getLightFactionIconSrc = (team) => `/icons/teams/${team}.webp`
const getDarkFactionIconSrc = (team) => `/icons/teams/${team}_dark.webp`
const getLightRoleIconSrc = (role) => `/icons/roles/${role}.png`
const getDarkRoleIconSrc = (role) => `/icons/roles/${role}_black.png`
const getLightMetricIconSrc = (metric) => `/icons/metrics/${metric}.png`
const getDarkMetricIconSrc = (metric) => `/icons/metrics/${metric}_black.png`

export const useThemedImages = () => {
    const theme = useTheme()
    const mode = theme.palette.mode
    return {
        getFactionIconSrc: mode === "dark" ? getLightFactionIconSrc : getDarkFactionIconSrc,
        getRoleIconSrc: mode === "dark" ? getLightRoleIconSrc : getDarkRoleIconSrc,
        getMetricIconSrc: mode === "dark" ? getLightMetricIconSrc : getDarkMetricIconSrc,
    }
}