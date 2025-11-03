import { useState } from 'react'

import './App.css'
import { Navigate, Route, Routes } from 'react-router-dom'
import Login from './components/auth/login'
import Chatbot from './components/pages/Chatbot'
import Signup from './components/auth/Signup'
import ForgotPassword from './components/auth/ForgotPass'
import Resetpassword from './components/auth/Reset-password'
import Profile from './components/pages/Profile'

function App() {


  return (
    <>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path='/chatbot' element={<Chatbot />} />
        <Route path='/signup' element={<Signup />} />
        <Route path='/login' element={<Login />} />
        <Route path='/forgot-password' element={<ForgotPassword />} />
        <Route path='/reset-password' element={<Resetpassword />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>

    </>
  )
}

export default App
