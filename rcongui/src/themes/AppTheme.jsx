import * as React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import getDefaultTheme from './default/getDefaultTheme';

function AppTheme(props) {
  const { children, disableCustomTheme, themeComponents, selectedScheme } = props;
  const [theme, setTheme] = React.useState(null);

  React.useEffect(() => {
    async function initializeTheme() {
      if (disableCustomTheme) {
        setTheme({});
        return;
      }

      const defaultTheme = await getDefaultTheme(themeComponents, selectedScheme);
      setTheme(createTheme(defaultTheme));
    }

    initializeTheme();
  }, [disableCustomTheme, themeComponents, selectedScheme]);

  if (disableCustomTheme) {
    return <React.Fragment>{children}</React.Fragment>;
  }

  if (!theme) {
    return null; // Or a loading indicator
  }
  
  return (
    <ThemeProvider theme={theme} colorSchemeStorageKey='crcon.colorScheme' modeStorageKey='crcon.colorMode' disableTransitionOnChange>
      {children}
    </ThemeProvider>
  );
}

export default AppTheme;