import * as React from "react";
import Avatar from "@mui/material/Avatar";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Footer from "./footer";
import { Alert, Stack } from "@mui/material";
import { Form, useSubmit, useActionData } from "react-router-dom";
import { useForm, Controller } from "react-hook-form";
import { createTheme, ThemeProvider, styled } from '@mui/material/styles';
import { redirect } from "react-router-dom";
import { execute, get } from "@/utils/fetchUtils";
import getDashboardTheme from "@/themes/getDashboardTheme"
import { useStorageState } from "@/hooks/useStorageState"

export const loader = async () => {
  const response = await get("is_logged_in");
  if (!response.ok) {
    let message = response.statusText;

    if (response.status === 504) {
      message += ". Your server is not responding.";
    }

    throw new Response(message, { status: response.status });
  }

  const json = await response.json();
  const authenticated = json.result.authenticated;

  if (authenticated) {
    return redirect("/");
  }

  return { authenticated };
};

export const action = async ({ request }) => {
  const { username, password } = Object.fromEntries(await request.formData());
  let isAuth = false;

  try {
    // this throws if 401
    const response = await execute("login", {
      username: username,
      password: password,
    });

    // this can also catch backend downtime
    if (!response.ok) {
      let message = response.statusText;

      if (response.status === 504) {
        message += ". Your server is not responding.";
      }

      return {
        error: response.status,
        message: message,
      };
    }

    const data = await response.json();
    isAuth = data.result;
  } catch (error) {
    // in case of 401
    if (error?.name === "InvalidLogin") {
      return {
        error: error.name,
        message: "Invalid login credentials. Try it again.",
      };
    }

    return {
      error: error,
      message: `Unknown error. Open the developer's tool in your browser, navigate to Network tab, record your activity and let us know about it.`,
    };
  }

  // success, redirect to the home page
  if (isAuth) {
    return redirect("/");
  }
};

const Wrapper = styled(Box)(({ theme }) => ({
  position: "relative",
  minHeight: "100vh",
  height: "100%",
  display: "flex",
  flexDirection: "column",
  [theme.breakpoints.up("md")]: {
    flexDirection: "row",
  },
}));

const HeroImageWrapper = styled(Box)(({ theme }) => ({
  flexBasis: "33vh",
  height: "100%",
  [theme.breakpoints.up("md")]: {
    flexBasis: "60%",
  },
}));

const HeroImage = styled("img")(({ theme }) => ({
  position: "absolute",
  top: 0,
  left: 0,
  objectFit: "cover",
  width: "100%",
  height: "33%",
  [theme.breakpoints.up("md")]: {
    height: "100%",
    width: "60%",
  },
}));

const MainWrapper = styled(Stack)(({ theme }) => ({
  flexBasis: "67vh",
  [theme.breakpoints.up("md")]: {
    flexBasis: "40%",
  },
}));

export default function Login() {
  const [loading, setLoading] = React.useState(false);
  const [mode] = useStorageState('crcon-mode', 'dark')

  const {
    handleSubmit,
    control,
    formState: { errors },
  } = useForm({
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const authError = useActionData();

  const submit = useSubmit();

  React.useEffect(() => setLoading(false), [authError]);

  const onSubmit = (values, e) => {
    setLoading(true);
    submit(e.target);
  };

  return (
    <ThemeProvider theme={createTheme(getDashboardTheme(mode))}>
      <HeroImage src="/hll15.webp" alt="" />
      <Wrapper>
        <HeroImageWrapper></HeroImageWrapper>
        <MainWrapper>
          <Container
            component="main"
            maxWidth="xs"
            sx={{ flexGrow: 1, display: "flex" }}
          >
            <CssBaseline />
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Avatar sx={{ m: 1, bgcolor: "secondary.main" }}>
                <LockOutlinedIcon />
              </Avatar>
              <Typography component="h1" variant="h5">
                Sign in
              </Typography>
              {authError && !loading && (
                <Box sx={{ py: 2, width: "100%" }}>
                  <Alert severity="error">{authError.message}</Alert>
                </Box>
              )}
              <Form method="POST" onSubmit={handleSubmit(onSubmit)}>
                <Controller
                  control={control}
                  name={"username"}
                  rules={{ required: "Username is required." }}
                  render={({ field }) => (
                    <TextField
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      value={field.value}
                      name={field.name}
                      inputRef={field.ref}
                      id="username"
                      label="Username"
                      margin="normal"
                      helperText={errors["username"]?.message}
                      error={!!errors["username"]}
                      autoComplete="username"
                      fullWidth
                    />
                  )}
                />
                <Controller
                  control={control}
                  name={"password"}
                  rules={{ required: "Password is required." }}
                  render={({ field }) => (
                    <TextField
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      value={field.value}
                      name={field.name}
                      inputRef={field.ref}
                      id="password"
                      type="password"
                      label="Password"
                      margin="normal"
                      helperText={errors["password"]?.message}
                      error={!!errors["password"]}
                      autoComplete="current-password"
                      fullWidth
                    />
                  )}
                />
                <Button
                  type="submit"
                  disabled={loading}
                  fullWidth
                  variant="contained"
                  sx={{ mt: 3, mb: 2 }}
                >
                  {loading ? "Authenticating..." : "Sign In"}
                </Button>
              </Form>
            </Box>
          </Container>
          <Stack justifyContent={"end"} sx={{ p: 3 }}>
            <Footer />
          </Stack>
        </MainWrapper>
      </Wrapper>
    </ThemeProvider>
  );
}
