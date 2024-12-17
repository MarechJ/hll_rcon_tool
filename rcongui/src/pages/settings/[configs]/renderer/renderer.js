import {materialObjectControlTester} from "@jsonforms/material-renderers";
import {anyOfNullTester, renderer as anyOfNullRenderer} from "./anyOfNull";
import {renderer as objectRenderer} from "./object";

export const customRenderers = [
  {
    tester: materialObjectControlTester,
    renderer: objectRenderer,
  },
  {tester: anyOfNullTester, renderer: anyOfNullRenderer},
]
