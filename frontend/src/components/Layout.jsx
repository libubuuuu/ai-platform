import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../store'
import {
  Search, ShoppingCart, Wand2, Image as ImageIcon,
  Upload, MessageSquare, LogOut, ShieldCheck
} from 'lucide-react'

const navItems = [
  { to: '/',         label: '内容发现',   icon: Search },
  { to: '/cart',     label: '购物车',     icon: ShoppingCart },
  { to: '/rewrite',  label: 'AI 洗稿',    icon: Wand2 },
  { to: '/image',    label: '图片画布',   icon: ImageIcon },
  { to: '/publish',  label: '一键发布',   icon: Upload, adminOnly: true },
  { to: '/comment',  label: '评论投放',   icon: MessageSquare, adminOnly: true },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen">
      <aside className="w-56 bg-slate-900 text-slate-200 flex flex-col">
        <div className="p-5 text-xl font-bold text-white border-b border-slate-700">
          AI Platform
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {navItems
            .filter((it) => !it.adminOnly || user?.is_admin)
            .map(({ to, label, icon: Icon, adminOnly }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition ${
                    isActive ? 'bg-brand-600 text-white' : 'hover:bg-slate-800'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{label}</span>
                {adminOnly && <ShieldCheck className="w-3 h-3 ml-auto text-yellow-400" />}
              </NavLink>
            ))}
        </nav>

        <div className="p-3 border-t border-slate-700 text-sm">
          <div className="px-3 py-2 text-slate-400">
            {user ? (
              <>
                <div>{user.username}</div>
                {user.is_admin && (
                  <div className="text-xs text-yellow-400 flex items-center gap-1 mt-1">
                    <ShieldCheck className="w-3 h-3" />管理员
                  </div>
                )}
              </>
            ) : '...'}
          </div>
          <button
            onClick={() => { logout(); navigate('/login') }}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-md hover:bg-slate-800 text-slate-300"
          >
            <LogOut className="w-4 h-4" /> 退出登录
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
