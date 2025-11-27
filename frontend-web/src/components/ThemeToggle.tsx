import React from 'react'
import { useTheme } from '../contexts/ThemeContext'

export default function ThemeToggle(){
  const { theme, toggle } = useTheme()
  return (
    <button onClick={toggle} aria-label="Toggle theme" style={{background:'transparent',border:'none',color:'inherit',cursor:'pointer'}}>
      {theme === 'dark' ? '🌙 Dark' : '☀️ Light'}
    </button>
  )
}
