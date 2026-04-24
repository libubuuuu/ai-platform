import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Wand2, Copy, CheckCheck } from 'lucide-react'
import { getCart, rewrite, listRewrites } from '../api'

const PLATFORMS = [
  { v: 'xiaohongshu', label: '小红书' },
  { v: 'douyin',      label: '抖音' },
  { v: 'bilibili',    label: 'B站' },
  { v: 'wechat_channel', label: '视频号' },
  { v: 'weibo',       label: '微博' },
  { v: 'zhihu',       label: '知乎' },
  { v: 'tieba',       label: '贴吧' },
]

export default function Rewrite() {
  const location = useLocation()
  const [cart, setCart] = useState([])
  const [selected, setSelected] = useState(location.state?.ids || [])
  const [targetPlatform, setTargetPlatform] = useState('xiaohongshu')
  const [mode, setMode] = useState('single')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])

  useEffect(() => {
    getCart().then((c) => setCart(c.items))
    listRewrites().then(setHistory)
  }, [])

  const toggle = (id) => {
    setSelected((s) => s.includes(id) ? s.filter((x) => x !== id) : [...s, id])
  }

  const doRewrite = async () => {
    if (selected.length === 0) return alert('请先选择内容')
    setLoading(true); setResult(null)
    try {
      const r = await rewrite({ content_ids: selected, target_platform: targetPlatform, mode })
      setResult(r)
      listRewrites().then(setHistory)
    } catch (e) {
      alert(e.response?.data?.detail || '洗稿失败。请检查 AI API Key 配置。')
    } finally { setLoading(false) }
  }

  return (
    <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* 左侧：选择 */}
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">AI 洗稿制作</h1>

        <div className="bg-white border rounded-lg p-4 space-y-3">
          <div>
            <label className="text-sm text-gray-600 block mb-1">目标平台</label>
            <select value={targetPlatform} onChange={(e) => setTargetPlatform(e.target.value)}
              className="w-full border rounded px-3 py-2">
              {PLATFORMS.map((p) => <option key={p.v} value={p.v}>{p.label}</option>)}
            </select>
          </div>

          <div>
            <label className="text-sm text-gray-600 block mb-1">洗稿模式</label>
            <div className="flex gap-2">
              {[
                { v: 'single', label: '一篇一洗（每篇独立输出）' },
                { v: 'merge',  label: '多篇合一（融合成一篇）' },
              ].map((m) => (
                <button key={m.v} onClick={() => setMode(m.v)}
                  className={`flex-1 px-3 py-2 text-xs rounded border ${mode === m.v ? 'bg-brand-600 text-white border-brand-600' : 'bg-white'}`}>
                  {m.label}
                </button>
              ))}
            </div>
          </div>

          <button onClick={doRewrite} disabled={loading || selected.length === 0}
            className="w-full bg-brand-600 text-white py-2 rounded disabled:opacity-50 flex items-center justify-center gap-1">
            <Wand2 className="w-4 h-4" /> {loading ? '洗稿中（约30秒）...' : `开始洗稿（已选 ${selected.length}）`}
          </button>
        </div>

        <div className="bg-white border rounded-lg p-4">
          <h3 className="text-sm font-semibold mb-2">从购物车选择要复刻的内容</h3>
          {cart.length === 0 && <p className="text-xs text-gray-400">购物车为空</p>}
          <div className="space-y-2 max-h-96 overflow-auto">
            {cart.map((it) => (
              <label key={it.id}
                className={`flex gap-2 p-2 rounded border cursor-pointer ${selected.includes(it.id) ? 'border-brand-500 bg-brand-50' : ''}`}>
                <input type="checkbox" checked={selected.includes(it.id)}
                  onChange={() => toggle(it.id)} className="mt-1" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{it.title || '(无标题)'}</div>
                  <div className="text-xs text-gray-500 truncate">{it.content_text}</div>
                  <div className="text-xs text-gray-400 mt-0.5">{it.platform} · {it.media_type}</div>
                </div>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* 右侧：结果 */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold">洗稿结果</h2>
        {result ? (
          <RewriteResult data={result} />
        ) : (
          <p className="text-gray-400 text-sm">在左侧选择内容并点击洗稿，结果会显示在这里。</p>
        )}

        {history.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold mt-6 mb-2">历史记录</h3>
            <div className="space-y-2">
              {history.slice(0, 10).map((h) => (
                <div key={h.id} className="bg-white border rounded p-3 cursor-pointer hover:shadow-sm"
                  onClick={() => setResult(h)}>
                  <div className="text-sm font-medium truncate">{h.title}</div>
                  <div className="text-xs text-gray-400">
                    {h.mode} · {h.ai_model} · {new Date(h.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function RewriteResult({ data }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(`${data.title}\n\n${data.content_text}`)
    setCopied(true); setTimeout(() => setCopied(false), 2000)
  }
  return (
    <div className="bg-white border rounded-lg p-4 space-y-3">
      <div className="flex justify-between items-start gap-2">
        <h3 className="font-semibold flex-1">{data.title}</h3>
        <button onClick={copy} className="p-2 text-gray-500 hover:text-brand-600">
          {copied ? <CheckCheck className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
        </button>
      </div>
      <p className="text-sm whitespace-pre-wrap leading-relaxed">{data.content_text}</p>

      {data.images?.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-1">复刻的图片（来自原文）：</p>
          <div className="flex gap-2 flex-wrap">
            {data.images.slice(0, 6).map((url, i) => (
              <img key={i} src={url} alt="" className="w-20 h-20 object-cover rounded border" />
            ))}
          </div>
        </div>
      )}

      {data.video_url && (
        <div>
          <p className="text-xs text-gray-500 mb-1">复刻的视频：</p>
          <video src={data.video_url} controls className="w-full max-h-64 rounded" />
        </div>
      )}

      <div className="text-xs text-gray-400">
        AI：{data.ai_provider} / {data.ai_model}
      </div>
    </div>
  )
}
