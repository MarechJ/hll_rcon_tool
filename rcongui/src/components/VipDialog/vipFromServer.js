import {fromJS} from "immutable";
import {reduce} from "lodash";

export function vipListFromServer(data) {
    return fromJS(
        reduce(
            data,
            (acc, val) => {
                acc[val.steam_id_64] = true;
                return acc;
            },
            {}
        )
    );
}
