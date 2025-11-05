import React, { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light'|'dark'

const ThemeContext = createContext<{ theme: Theme; toggle: ()=>void }>({ theme: 'light', toggle: ()=>{} })

export const ThemeProvider = ({ children }: { children: React.ReactNode }) =>{
  const [theme, setTheme] = useState<Theme>(()=>{
    const saved = typeof window !== 'undefined' ? localStorage.getItem('bf:theme') : null
    return (saved as Theme) || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
  })

  useEffect(()=>{
    document.documentElement.setAttribute('data-theme', theme)
    try{ localStorage.setItem('bf:theme', theme) }catch(e){}
  },[theme])

  function toggle(){ setTheme(t=> t==='light' ? 'dark' : 'light') }

  return <ThemeContext.Provider value={{ theme, toggle }}>{children}</ThemeContext.Provider>
}

export const useTheme = ()=> useContext(ThemeContext)
