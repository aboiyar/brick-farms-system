import React from 'react'

export default function Input(props: React.InputHTMLAttributes<HTMLInputElement>){
  return <input {...props} style={{ padding:8, borderRadius:8, border:'1px solid #ddd', width:'100%', boxSizing:'border-box' }} />
}
