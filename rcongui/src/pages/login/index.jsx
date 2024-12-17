import Avatar from '@mui/material/Avatar'
import Button from '@mui/material/Button'
import CssBaseline from '@mui/material/CssBaseline'
import TextField from '@mui/material/TextField'
import Box from '@mui/material/Box'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import Typography from '@mui/material/Typography'
import Container from '@mui/material/Container'
import Footer from './footer'
import { Alert, Stack } from '@mui/material'
import { Form, useSubmit, useActionData, useLoaderData } from 'react-router-dom'
import { useForm, Controller } from 'react-hook-form'
import { createTheme, ThemeProvider, styled } from '@mui/material/styles'
import { redirect } from 'react-router-dom'
import { cmd } from '@/utils/fetchUtils'
import getDashboardTheme from '@/themes/getDashboardTheme'
import { useStorageState } from '@/hooks/useStorageState'
import { useEffect, useState } from 'react'

export const loader = async ({ request }) => {
  let user
  const url = new URL(request.url)
  const from = url.searchParams.get('from') || '/'

  try {
    user = await cmd.IS_AUTHENTICATED({ throwRouteError: false })
  } catch (error) {
    return {
      error: error,
      message: error?.text
    }
  }

  if (user.authenticated) {
    return redirect(from)
  }

  return { authenticated: user.authenticated, from }
}

export const action = async ({ request }) => {
  const formData = await request.formData()
  const { username, password } = Object.fromEntries(formData)
  const from = formData.get('from') || '/'
  let isAuth = false

  try {
    const { result } = await cmd.AUTHENTICATE({
      payload: {
        username: username,
        password: password
      },
      throwRouteError: false
    })
    isAuth = result
  } catch (error) {
    console.log(error)
    if (error.status === 401) {
      return {
        error: error.name,
        message: 'Invalid login credentials. Try it again.'
      }
    }

    return {
      error: error,
      message: `Unknown error. Open the developer's tool in your browser, navigate to Network tab, record your activity and let us know about it.`
    }
  }

  if (isAuth) {
    return redirect(from)
  }
}

const Wrapper = styled(Box)(({ theme }) => ({
  position: 'relative',
  minHeight: '100vh',
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  [theme.breakpoints.up('md')]: {
    flexDirection: 'row'
  }
}))

const HeroImageWrapper = styled(Box)(({ theme }) => ({
  flexBasis: '33vh',
  height: '100%',
  [theme.breakpoints.up('md')]: {
    flexBasis: '60%'
  }
}))

const HeroImage = styled('img')(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  objectFit: 'cover',
  width: '100%',
  height: '33%',
  [theme.breakpoints.up('md')]: {
    height: '100%',
    width: '60%'
  }
}))

const MainWrapper = styled(Stack)(({ theme }) => ({
  flexBasis: '67vh',
  [theme.breakpoints.up('md')]: {
    flexBasis: '40%'
  }
}))

export default function Login() {
  const [loading, setLoading] = useState(false)
  const [mode] = useStorageState('mode', 'dark')

  const {
    handleSubmit,
    control,
    formState: { errors }
  } = useForm({
    defaultValues: {
      username: '',
      password: ''
    }
  })

  const authError = useActionData()
  const data = useLoaderData()
  const { from } = useLoaderData()

  const submit = useSubmit()

  useEffect(() => setLoading(false), [authError])

  const onSubmit = (values, e) => {
    setLoading(true)
    submit(e.target)
  }

  return (
    <ThemeProvider theme={createTheme(getDashboardTheme(mode))}>
      <HeroImage src='/hll15.webp' alt='' />
      <Wrapper>
        <HeroImageWrapper></HeroImageWrapper>
        <MainWrapper>
          <Container component='main' maxWidth='xs' sx={{ flexGrow: 1, display: 'flex' }}>
            <CssBaseline />
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
                <LockOutlinedIcon />
              </Avatar>
              <Typography component='h1' variant='h5'>
                Sign in
              </Typography>
              {data.error ? (
                <Box sx={{ py: 2, width: '100%' }}>
                  <Alert severity='error'>{data.message}</Alert>
                </Box>
              ) : authError && !loading ? (
                <Box sx={{ py: 2, width: '100%' }}>
                  <Alert severity='error'>{authError.message}</Alert>
                </Box>
              ) : null}
              <Form method='POST' onSubmit={handleSubmit(onSubmit)}>
                <input type='hidden' name='from' value={from} />
                <Controller
                  control={control}
                  name={'username'}
                  rules={{ required: 'Username is required.' }}
                  render={({ field }) => (
                    <TextField
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      value={field.value}
                      name={field.name}
                      inputRef={field.ref}
                      id='username'
                      label='Username'
                      margin='normal'
                      helperText={errors['username']?.message}
                      error={!!errors['username']}
                      autoComplete='username'
                      fullWidth
                    />
                  )}
                />
                <Controller
                  control={control}
                  name={'password'}
                  rules={{ required: 'Password is required.' }}
                  render={({ field }) => (
                    <TextField
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      value={field.value}
                      name={field.name}
                      inputRef={field.ref}
                      id='password'
                      type='password'
                      label='Password'
                      margin='normal'
                      helperText={errors['password']?.message}
                      error={!!errors['password']}
                      autoComplete='current-password'
                      fullWidth
                    />
                  )}
                />
                <Button type='submit' disabled={loading} fullWidth variant='contained' sx={{ mt: 3, mb: 2 }}>
                  {loading ? 'Authenticating...' : 'Sign In'}
                </Button>
              </Form>
            </Box>
          </Container>
          <Stack justifyContent={'end'} sx={{ p: 3 }}>
            <Footer />
          </Stack>
        </MainWrapper>
      </Wrapper>
    </ThemeProvider>
  )
}
