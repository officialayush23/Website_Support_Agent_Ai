import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import ThemeProvider from './components/use_ui/theme-provider.jsx'
import { AuthProvider } from './components/AuthHandlers/AuthContext.jsx'


createRoot(document.getElementById('root')).render(

  <BrowserRouter>
    <ThemeProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </ThemeProvider>
  </BrowserRouter>

)
