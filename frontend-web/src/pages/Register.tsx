import React, { useState } from 'react'
import { signup, storeToken } from '../api/auth'
import { useNavigate } from 'react-router-dom'

export default function RegisterPage(){
  const [tenant,setTenant]=useState('')
  const [email,setEmail]=useState('')
  const [password,setPassword]=useState('')
  const [error,setError]=useState<string|null>(null)
  const nav = useNavigate()

  async function submit(e:React.FormEvent){
    e.preventDefault()
    setError(null)
    try{
      const res = await signup(tenant,email,password)
      storeToken(res.access_token)
      nav('/')
    }catch(err:any){ setError(err.message || 'Signup failed') }
  }

  return (
    <div>
      <h3>Register</h3>
      <form onSubmit={submit}>
        <div>
          <label>Tenant name</label>
          <input value={tenant} onChange={e=>setTenant(e.target.value)} />
        </div>
        <div>
          <label>Email</label>
          <input value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div>
          <label>Password</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <button type="submit">Register</button>
        {error && <div style={{color:'red'}}>{error}</div>}
      </form>
    </div>
  )
}
