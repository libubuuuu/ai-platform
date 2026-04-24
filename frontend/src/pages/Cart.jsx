import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Trash2, X, Wand2 } from 'lucide-react'
import { getCart, removeFromCart, clearCart } from '../api'

export default function Cart() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const reload = async () => {
    setLoading(true)
    try { setItems((await getCart()).items) }
    finally { setLoading(false) }
  }
  useEffect(() => { reload() }, [])

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">购物车（{items.length}）</h1>
        <div className="flex gap-2">
          {items.length > 0 && (
            <button onClick={async () => { await clearCart(); reload() }}
              className="px-3 py-2 bg-white border rounded-md text-sm flex items-center gap-1">
              <Trash2 className="w-4 h-4" /> 清空
            </button>
          )}
          <button onClick={() => navigate('/rewrite', { state: { ids: items.map((i) => i.id) } })}
            disabled={items.length === 0}
            className="px-4 py-2 bg-brand-600 text-white rounded-md flex items-center gap-1 disabled:opacity-50">
            <Wand2 className="w-4 h-4" /> 进入洗稿制作
          </button>
        </div>
      </div>

      {loading ? (
        <p className="text-gray-400 text-sm">加载中...</p>
      ) : items.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          购物车是空的。去<a href="/" className="text-brand-600 underline">内容发现</a>页面添加吧。
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((it) => (
            <div key={it.id} className="flex items-center gap-3 bg-white border rounded-lg p-3">
              {(it.video_cover || it.images?.[0]) && (
                <img src={it.video_cover || it.images[0]} alt=""
                  className="w-16 h-16 object-cover rounded" />
              )}
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium truncate">{it.title || '(无标题)'}</h3>
                <p className="text-xs text-gray-500 truncate">{it.content_text}</p>
                <p className="text-xs text-gray-400 mt-1">
                  {it.platform} · {it.media_type} · 👍 {it.likes}
                </p>
              </div>
              <button onClick={async () => { await removeFromCart(it.id); reload() }}
                className="p-2 text-gray-400 hover:text-red-500">
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
