import {materialObjectControlTester} from "@jsonforms/material-renderers";
import {anyOfNullTester, renderer as anyOfNullRenderer} from "./anyOfNull";
import {renderer as objectRenderer} from "./object";
import {levelThresholdsTester, renderer as levelThresholdsRenderer} from "./levelThresholds";
import {seedVipListTester, renderer as seedVipListRenderer} from "./seedVipList";

export const customRenderers = [
  {tester: seedVipListTester, renderer: seedVipListRenderer},
  {tester: levelThresholdsTester, renderer: levelThresholdsRenderer},
  {
    tester: materialObjectControlTester,
    renderer: objectRenderer,
  },
  {tester: anyOfNullTester, renderer: anyOfNullRenderer},
]
