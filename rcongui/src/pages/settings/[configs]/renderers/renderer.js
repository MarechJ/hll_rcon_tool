import {materialObjectControlTester} from "@jsonforms/material-renderers";
import {anyOfNullTester, renderer as anyOfNullRenderer} from "./anyOfNull";
import {renderer as additionalPropertiesRenderer} from "./additionalProperties";

export const customRenderers = [
  {
    tester: materialObjectControlTester,
    renderer: additionalPropertiesRenderer,
  },
  {tester: anyOfNullTester, renderer: anyOfNullRenderer},
]
