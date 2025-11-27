import React, { useState } from 'react'
import { login, storeToken } from '../api/auth'
import { useNavigate } from 'react-router-dom'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'

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
      <form onSubmit={submit} style={{maxWidth:420}}>
        <div style={{marginBottom:8}}>
          <label>Email</label>
          <Input value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div style={{marginBottom:8}}>
          <label>Password</label>
          <Input type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <div style={{display:'flex',gap:8}}>
          <Button type="submit">Login</Button>
        </div>
        {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
      </form>
    </div>
  )
}
