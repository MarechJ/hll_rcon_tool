import { cmd } from "@/utils/fetchUtils";
import { gameSwitch } from "@/utils/lib";

const HLL_TIMERS = {
    match: {
        warfare: {
            min: 30,
            max: 180,
            default: 90,
        },
        offensive: {
            min: 10,
            max: 60,
            default: 30,
        },
        skirmish: {
            min: 10,
            max: 60,
            default: 30,
        },
    },
    warmup: {
        warfare: {
            min: 1,
            max: 10,
            default: 3,
        },
        skirmish: {
            min: 1,
            max: 10,
            default: 3,
        },
    },
}

const HLLV_TIMERS = {
    match: {
        warfare: {
            min: 30,
            max: 180,
            default: 90,
        },
        offensive: {
            min: 10,
            max: 60,
            default: 30,
        },
        domination: {
            min: 10,
            max: 60,
            default: 30,
        },
        conquest: {
            min: 30,
            max: 180,
            default: 90,
        },
    },
    warmup: {
        warfare: {
            min: 1,
            max: 10,
            default: 3,
        },
        domination: {
            min: 1,
            max: 10,
            default: 3,
        },
        conquest: {
            min: 1,
            max: 10,
            default: 3,
        },
    },
}

export const loader = async () => {
    const maps = await cmd.GET_MAPS();
    const timers = gameSwitch(HLL_TIMERS, HLLV_TIMERS)
    return { timers, maps }
}
