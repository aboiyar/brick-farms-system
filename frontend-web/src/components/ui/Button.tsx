import React from 'react'

export default function Button({ children, onClick, variant='primary', type='button' }: { children: React.ReactNode; onClick?: ()=>void; variant?: 'primary'|'secondary'|'ghost'; type?: 'button'|'submit' }){
  const base = {
    primary: { background: 'var(--green-700)', color:'#fff', border:'none' },
    secondary: { background: 'var(--brown-500)', color:'#fff', border:'none' },
    ghost: { background:'transparent', color:'var(--text)', border:'1px solid rgba(0,0,0,0.08)'}
  } as any
  const style = { padding:'8px 12px', borderRadius:8, fontWeight:600, cursor:'pointer', ...base[variant] }
  return <button type={type} onClick={onClick} style={style}>{children}</button>
}
