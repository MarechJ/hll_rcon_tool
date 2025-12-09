import {materialObjectControlTester} from "@jsonforms/material-renderers";
import {anyOfNullTester, renderer as anyOfNullRenderer} from "./anyOfNull";
import {renderer as objectRenderer} from "./object";
import {levelThresholdsTester, renderer as levelThresholdsRenderer} from "./levelThresholds";

export const customRenderers = [
  {tester: levelThresholdsTester, renderer: levelThresholdsRenderer},
  {
    tester: materialObjectControlTester,
    renderer: objectRenderer,
  },
  {tester: anyOfNullTester, renderer: anyOfNullRenderer},
]
