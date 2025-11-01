import { useState } from 'react'

import './App.css'
import { Navigate, Route, Routes } from 'react-router-dom'
import Login from './components/auth/login'
import Chatbot from './components/pages/Chatbot'
import Signup from './components/auth/Signup'
import ForgotPassword from './components/auth/ForgotPass'

function App() {


  return (
    <>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path='/chatbot' element={<Chatbot />} />
        <Route path='/signup' element={<Signup />} />
        <Route path='/login' element={<Login />} />
        <Route path='/forgot-password' element={<ForgotPassword />} />
      </Routes>

    </>
  )
}

export default App
