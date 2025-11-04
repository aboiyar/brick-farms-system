import React, { createContext, useContext, useEffect, useState } from 'react'
import { getToken, parseJwt, storeToken, logout as doLogout } from '../api/auth'

type User = { sub?: string; tenant_id?: string; role?: string } | null

const AuthContext = createContext<{ user: User; setToken: (t: string)=>void; logout: ()=>void }>({ user: null, setToken: ()=>{}, logout: ()=>{} })

export const AuthProvider = ({ children }: { children: React.ReactNode }) =>{
  const [user, setUser] = useState<User>(null)

  useEffect(()=>{
    const t = getToken()
    if(t){ setUser(parseJwt(t)) }
  }, [])

  function setToken(t:string){ storeToken(t); setUser(parseJwt(t)) }
  function logout(){ doLogout(); setUser(null) }

  return <AuthContext.Provider value={{ user, setToken, logout }}>{children}</AuthContext.Provider>
}

export const useAuth = ()=> useContext(AuthContext)
