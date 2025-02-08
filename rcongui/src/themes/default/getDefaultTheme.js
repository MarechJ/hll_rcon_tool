import {
  dataDisplayCustomizations,
  feedbackCustomizations,
  navigationCustomizations,
  surfacesCustomizations,
  // inputsCustomizations,
} from "./customizations";

async function getColorPrimitives(schemeName) {
  switch (schemeName) {
    case "github":
      return import("./primitives/github");
    case "highContrast":
      return import("./primitives/highContrast");
    case "lime":
      return import("./primitives/lime");
    default:
      return import("./primitives/default");
  }
}

export default async function getDefaultTheme(themeComponents, selectedScheme = "default") {
  const {
    brand,
    gray,
    green,
    orange,
    red,
    typography,
    shadows,
    shape,
    colorSchemes,
  } = await getColorPrimitives(selectedScheme);

  const colors = { brand, gray, green, orange, red };

  return {
    // For more details about CSS variables configuration, see https://mui.com/material-ui/customization/css-theme-variables/configuration/
    cssVariables: {
      colorSchemeSelector: "data-mui-color-scheme",
      cssVarPrefix: "template",
    },
    colorSchemes, // Recently added in v6 for building light & dark mode app, see https://mui.com/material-ui/customization/palette/#color-schemes
    typography,
    shadows,
    shape,
    components: {
      ...dataDisplayCustomizations(colors),
      ...feedbackCustomizations(colors),
      ...navigationCustomizations(colors),
      ...surfacesCustomizations(colors),
      // This needs to be worked on
      // ...inputsCustomizations(colors),
      ...themeComponents,
    },
  };
}