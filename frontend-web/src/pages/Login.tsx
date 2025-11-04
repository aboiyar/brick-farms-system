import React, { useState } from 'react'
import { login, storeToken } from '../api/auth'
import { useNavigate } from 'react-router-dom'

export default function LoginPage(){
  const [email,setEmail]=useState('')
  const [password,setPassword]=useState('')
  const [error,setError]=useState<string|null>(null)
  const nav = useNavigate()

  async function submit(e:React.FormEvent){
    e.preventDefault()
    setError(null)
    try{
      const res = await login(email,password)
      storeToken(res.access_token)
      nav('/')
    }catch(err:any){ setError(err.message || 'Login failed') }
  }

  return (
    <div>
      <h3>Login</h3>
      <form onSubmit={submit}>
        <div>
          <label>Email</label>
          <input value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div>
          <label>Password</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <button type="submit">Login</button>
        {error && <div style={{color:'red'}}>{error}</div>}
      </form>
    </div>
  )
}
