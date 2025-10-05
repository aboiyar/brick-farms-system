const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1'

type ReqOpts = RequestInit & { json?: any }

async function request(path: string, opts: ReqOpts = {}) {
  const url = path.startsWith('http') ? path : `${BASE}${path.startsWith('/') ? '' : '/'}${path}`
  const headers: Record<string,string> = opts.headers ? {...(opts.headers as Record<string,string>)} : {}
  if (opts.json) {
    headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(opts.json)
  }
  const res = await fetch(url, {...opts, headers, credentials: 'include'})
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`)
  return res.json().catch(()=>null)
}

export const api = {
  get: (p: string) => request(p, { method: 'GET' }),
  post: (p: string, json: any) => request(p, { method: 'POST', json }),
  put: (p: string, json: any) => request(p, { method: 'PUT', json }),
  del: (p: string) => request(p, { method: 'DELETE' })
}

export default api
