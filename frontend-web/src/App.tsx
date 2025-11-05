import React, { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import MapView from './components/MapView'
import { fetchTasksWithGeom } from './api/tasks'
import { AuthProvider } from './contexts/AuthContext'
import LoginPage from './pages/Login'
import RegisterPage from './pages/Register'
import { ThemeProvider } from './contexts/ThemeContext'
import ThemeToggle from './components/ThemeToggle'

const Home = () => {
  const [tasks, setTasks] = useState<any>(null)
  useEffect(()=>{ fetchTasksWithGeom().then(setTasks).catch(()=>{}) }, [])
  return (
    <div>
      <h2>BrickFarm Task Map</h2>
      <MapView tasks={tasks} />
    </div>
  )
}

const Admin = ()=> <div><h3>Admin Dashboard (placeholder)</h3></div>
const Agronomist = ()=> <div><h3>Agronomist Dashboard (placeholder)</h3></div>
const Investor = ()=> <div><h3>Investor Dashboard (placeholder)</h3></div>

function App(){
  return (
    <AuthProvider>
      <ThemeProvider>
        <div className="app-shell">
          <header className="app-header">
            <div style={{display:'flex',alignItems:'center',gap:12}}>
              <strong>BrickFarm</strong>
              <nav className="app-nav">
                <Link to="/">Home</Link>
                <Link to="/dashboard/admin">Admin</Link>
              </nav>
            </div>
            <div style={{display:'flex',alignItems:'center',gap:12}}>
              <ThemeToggle />
            </div>
          </header>
          <main className="app-main">
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<Home/>} />
                <Route path="/login" element={<LoginPage/>} />
                <Route path="/register" element={<RegisterPage/>} />
                <Route path="/dashboard/admin" element={<Admin/>} />
                <Route path="/dashboard/agronomist" element={<Agronomist/>} />
                <Route path="/dashboard/investor" element={<Investor/>} />
              </Routes>
            </BrowserRouter>
          </main>
        </div>
      </ThemeProvider>
    </AuthProvider>
  )
}

export default App
