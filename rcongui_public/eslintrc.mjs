import { fixupConfigRules, fixupPluginRules } from "@eslint/compat";
import unusedImports from "eslint-plugin-unused-imports";
import react from "eslint-plugin-react";
import typescriptEslint from "@typescript-eslint/eslint-plugin";
import _import from "eslint-plugin-import";
import prettier from "eslint-plugin-prettier";
import globals from "globals";
import tsParser from "@typescript-eslint/parser";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

export default [...fixupConfigRules(compat.extends(
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:import/recommended",
    "plugin:import/typescript",
    "plugin:prettier/recommended",
    "plugin:react-hooks/recommended",
    "prettier",
)), {
    plugins: {
        "unused-imports": unusedImports,
        react: fixupPluginRules(react),
        "@typescript-eslint": fixupPluginRules(typescriptEslint),
        import: fixupPluginRules(_import),
        prettier: fixupPluginRules(prettier),
    },

    languageOptions: {
        globals: {
            ...globals.browser,
            ...globals.node,
        },

        parser: tsParser,
    },

    settings: {
        "import/resolver": {
            typescript: true,
        },
    },

    rules: {
        "import/default": 0,
        "import/no-named-as-default-member": 0,
        "import/no-unresolved": "warn",
        "no-unused-vars": "off",
        "react/react-in-jsx-scope": "off",
        "@typescript-eslint/ban-ts-comment": "off",
        "unused-imports/no-unused-imports": "warn",
        "react/prop-types": "off",
    },
}];