import { useEffect, useState } from 'react'
import { Search, Plus, Flame, TrendingUp, Zap, Video, Image as ImgIcon, FileText } from 'lucide-react'
import { listPlatforms, searchContent, fetchTrending, addToCart } from '../api'
import { useRegion } from '../store'

const HEAT_TAGS = {
  hot:              { label: '热门',   icon: Flame,      cls: 'tag-hot' },
  rising:           { label: '潜力',   icon: TrendingUp, cls: 'tag-rising' },
  predicted_viral:  { label: '预爆',   icon: Zap,        cls: 'tag-predicted_viral' },
  normal:           { label: '一般',   icon: null,       cls: 'tag-normal' },
}

const MEDIA_ICONS = { text: FileText, image: ImgIcon, video: Video, mixed: ImgIcon }

export default function Discovery() {
  const { region, setRegion, platform, setPlatform } = useRegion()
  const [platforms, setPlatforms] = useState({ domestic: [], international: [] })
  const [keyword, setKeyword] = useState('')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [insight, setInsight] = useState('')

  useEffect(() => { listPlatforms().then(setPlatforms) }, [])

  const currentList = region === 'domestic' ? platforms.domestic : platforms.international

  const doSearch = async () => {
    if (!keyword.trim()) return
    setLoading(true); setInsight('')
    try {
      const res = await searchContent({ platform, keyword, limit: 20, sort: 'hot' })
      setItems(res)
      if (res.length > 0) setInsight(res[0].keyword_insight || '')
    } catch (e) {
      alert(e.response?.data?.detail || '搜索失败。请确认后端已启动且 MediaCrawler 已配置。')
    } finally { setLoading(false) }
  }

  const doTrending = async () => {
    setLoading(true)
    try {
      setItems(await fetchTrending({ platform, limit: 20 }))
    } catch (e) {
      alert(e.response?.data?.detail || '获取热门失败')
    } finally { setLoading(false) }
  }

  const onAdd = async (id) => {
    try { await addToCart(id); alert('已加入购物车') }
    catch (e) { alert(e.response?.data?.detail || '加入失败') }
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">内容发现</h1>

      {/* 国内/国外 切换 */}
      <div className="flex gap-2">
        {['domestic', 'international'].map((r) => (
          <button key={r} onClick={() => setRegion(r)}
            className={`px-4 py-2 rounded-md ${region === r ? 'bg-brand-600 text-white' : 'bg-white border'}`}>
            {r === 'domestic' ? '🇨🇳 国内' : '🌍 国外'}
          </button>
        ))}
      </div>

      {/* 平台细选 */}
      <div className="flex flex-wrap gap-2">
        {currentList.map((p) => (
          <button key={p} onClick={() => setPlatform(p)}
            className={`px-3 py-1.5 rounded-md text-sm ${platform === p ? 'bg-slate-900 text-white' : 'bg-white border'}`}>
            {p}
          </button>
        ))}
      </div>

      {/* 搜索栏 */}
      <div className="flex gap-2">
        <div className="flex-1 flex items-center bg-white border rounded-md px-3">
          <Search className="w-4 h-4 text-gray-400" />
          <input value={keyword} onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && doSearch()}
            placeholder="输入关键词搜索..."
            className="flex-1 px-2 py-2 outline-none" />
        </div>
        <button onClick={doSearch} disabled={loading}
          className="px-4 py-2 bg-brand-600 text-white rounded-md disabled:opacity-50">搜索</button>
        <button onClick={doTrending} disabled={loading}
          className="px-4 py-2 bg-white border rounded-md">热门榜单</button>
      </div>

      {/* AI 关键词洞察 */}
      {insight && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-md text-sm text-amber-800">
          💡 <b>AI 关键词分析：</b>{insight}
        </div>
      )}

      {/* 结果网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((it) => {
          const Tag = HEAT_TAGS[it.heat_tag] || HEAT_TAGS.normal
          const MediaIcon = MEDIA_ICONS[it.media_type] || FileText
          return (
            <div key={it.id} className="bg-white rounded-lg border p-4 space-y-2 hover:shadow-md transition">
              <div className="flex items-start justify-between gap-2">
                <h3 className="font-semibold text-sm line-clamp-2 flex-1">{it.title || '(无标题)'}</h3>
                <span className={`px-2 py-0.5 rounded text-xs flex items-center gap-1 shrink-0 ${Tag.cls}`}>
                  {Tag.icon && <Tag.icon className="w-3 h-3" />}{Tag.label}
                </span>
              </div>

              {it.video_cover && (
                <img src={it.video_cover} alt="" className="w-full h-40 object-cover rounded" />
              )}
              {!it.video_cover && it.images?.[0] && (
                <img src={it.images[0]} alt="" className="w-full h-40 object-cover rounded" />
              )}

              <p className="text-xs text-gray-500 line-clamp-3">{it.content_text}</p>

              <div className="flex items-center justify-between text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <MediaIcon className="w-3 h-3" />
                  {it.media_type}
                </span>
                <span>👍 {it.likes} · 💬 {it.comments} · 🔄 {it.shares}</span>
              </div>

              <div className="flex gap-2 pt-1">
                <a href={it.source_url} target="_blank" rel="noreferrer"
                  className="flex-1 text-center text-xs py-1.5 border rounded hover:bg-gray-50">查看原文</a>
                <button onClick={() => onAdd(it.id)}
                  className="flex-1 text-xs py-1.5 bg-brand-600 text-white rounded hover:bg-brand-700 flex items-center justify-center gap-1">
                  <Plus className="w-3 h-3" />加入购物车
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {!loading && items.length === 0 && (
        <div className="text-center py-12 text-gray-400 text-sm">
          还没有搜索结果。输入关键词或点击"热门榜单"开始。
        </div>
      )}
    </div>
  )
}
