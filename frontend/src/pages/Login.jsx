import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, me } from '../api'
import { useAuth } from '../store'

export default function Login() {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState('')
  const { setToken, setUser } = useAuth()
  const navigate = useNavigate()

  const onSubmit = async (e) => {
    e.preventDefault()
    setErr(''); setLoading(true)
    try {
      const { access_token } = await login(username, password)
      setToken(access_token)
      const u = await me()
      setUser(u)
      navigate('/')
    } catch (e) {
      setErr(e.response?.data?.detail || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-brand-700">
      <form onSubmit={onSubmit} className="bg-white rounded-xl shadow-xl p-8 w-96 space-y-4">
        <h1 className="text-2xl font-bold text-center">AI Platform</h1>
        <p className="text-sm text-gray-500 text-center">多平台内容智能运营系统</p>

        <div>
          <label className="block text-sm text-gray-600 mb-1">用户名</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-brand-500" />
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">密码</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-brand-500" />
        </div>

        {err && <p className="text-red-500 text-sm">{err}</p>}

        <button type="submit" disabled={loading}
          className="w-full bg-brand-600 hover:bg-brand-700 text-white py-2 rounded-md disabled:opacity-50">
          {loading ? '登录中…' : '登录'}
        </button>

        <p className="text-xs text-gray-400 text-center">
          默认账号：admin / 密码见 backend/.env 的 ADMIN_PASSWORD
        </p>
      </form>
    </div>
  )
}
