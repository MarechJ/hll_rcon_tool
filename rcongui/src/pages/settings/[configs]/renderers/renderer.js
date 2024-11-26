import {anyOfNullTester, renderer as anyOfNullRenderer} from "./anyOfNull";
import {renderer as objectRenderer} from "./object";
import {materialObjectControlTester} from "@jsonforms/material-renderers";

export const customRenderers = [
  {
    tester: materialObjectControlTester,
    renderer: objectRenderer,
  },
  {tester: anyOfNullTester, renderer: anyOfNullRenderer},
]
