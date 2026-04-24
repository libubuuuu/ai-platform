import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './store'
import { me } from './api'
import Layout from './components/Layout'
import Login from './pages/Login'
import Discovery from './pages/Discovery'
import Cart from './pages/Cart'
import Rewrite from './pages/Rewrite'
import ImageCanvas from './pages/ImageCanvas'
import Publish from './pages/Publish'
import Comment from './pages/Comment'

function PrivateRoute({ children, adminOnly = false }) {
  const { token, user } = useAuth()
  if (!token) return <Navigate to="/login" replace />
  if (adminOnly && user && !user.is_admin) return <Navigate to="/" replace />
  return children
}

export default function App() {
  const { token, setUser, logout } = useAuth()

  useEffect(() => {
    if (token) {
      me().then(setUser).catch(() => logout())
    }
  }, [token])

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<PrivateRoute><Layout /></PrivateRoute>}>
        <Route index element={<Discovery />} />
        <Route path="cart" element={<Cart />} />
        <Route path="rewrite" element={<Rewrite />} />
        <Route path="image" element={<ImageCanvas />} />
        <Route path="publish" element={<PrivateRoute adminOnly><Publish /></PrivateRoute>} />
        <Route path="comment" element={<PrivateRoute adminOnly><Comment /></PrivateRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
