import { fromJS } from "immutable";
import reduce from "lodash/reduce";

export function vipListFromServer(data) {
  return fromJS(
    reduce(
      data,
      (acc, val) => {
        acc[val.player_id] = true;
        return acc;
      },
      {}
    )
  );
}
