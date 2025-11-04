import { api } from './client'

type TokenResp = { access_token: string; refresh_token?: string; token_type?: string }

export async function login(email: string, password: string): Promise<TokenResp> {
  return api.post('/auth/token', { email, password })
}

export async function signup(tenant_name: string, email: string, password: string): Promise<TokenResp> {
  return api.post('/auth/signup', { tenant_name, email, password })
}

export function storeToken(token: string){
  localStorage.setItem('bf_access_token', token)
}

export function getToken(){
  return localStorage.getItem('bf_access_token')
}

export function parseJwt(token?: string){
  if(!token) return null
  try{
    const payload = token.split('.')[1]
    const decoded = JSON.parse(atob(payload.replace(/-/g,'+').replace(/_/g,'/')))
    return decoded
  }catch(e){ return null }
}

export function logout(){
  localStorage.removeItem('bf_access_token')
}
