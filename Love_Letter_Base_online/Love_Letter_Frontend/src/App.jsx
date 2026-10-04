import React from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import Register from "./pages/Register"
import Home from "./pages/Home"
import NotFound from "./pages/NotFound"
import ProtectedRoute from "./components/ProtectedRoute"
import Tutorial from "./pages/Tutorial"
import Profile from "./pages/Profile"
import Header from "./components/Header"
import About from "./pages/About"
import Play from "./pages/Play"
import "./styles/App.css"

function Logout() {
  localStorage.clear()
  return <Navigate to="/login/" />
}

function RegisterAndLogout() {
  localStorage.clear()
  return <Register />
}
function App() {
  return (
    <>
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/play"
            element={<ProtectedRoute>
              <Play />
            </ProtectedRoute>} />
          <Route path="/tutorial" element={<Tutorial />} />
          <Route path="/about" element={<About />} />
          <Route path="/id" element={<Profile />} />
          <Route path="/login" element={<Login />} />
          <Route path="/logout" element={<Logout />} />
          <Route path="/register" element={<RegisterAndLogout />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
