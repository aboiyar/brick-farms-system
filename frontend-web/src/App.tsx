import React from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import MapView from './components/MapView'

const Home = () => (
  <div>
    <h2>BrickFarm Task Map</h2>
    <MapView />
  </div>
)

const Login = () => (
  <div>
    <h3>Login (skeleton)</h3>
    <p>Form goes here</p>
  </div>
)

const Register = () => (
  <div>
    <h3>Register (skeleton)</h3>
    <p>Form goes here</p>
  </div>
)

function App(){
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link> | <Link to="/login">Login</Link> | <Link to="/register">Register</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home/>} />
        <Route path="/login" element={<Login/>} />
        <Route path="/register" element={<Register/>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
