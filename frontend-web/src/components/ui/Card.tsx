import React from 'react'

export default function Card({ children, style = {} }: { children: React.ReactNode; style?: React.CSSProperties }){
  return (
    <div style={{borderRadius:12, padding:16, background:'var(--bg)', boxShadow:'0 1px 6px rgba(0,0,0,0.06)', border:'1px solid rgba(0,0,0,0.04)', ...style}}>
      {children}
    </div>
  )
}
