import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './app'
import './styles/globals.css'
import './i18n/config'
import './lib/runtimeConfig'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(<App />)
