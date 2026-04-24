import { useState } from 'react'
import { MessageSquare, Copy, ShieldCheck, AlertTriangle } from 'lucide-react'
import { suggestComments } from '../api'

export default function Comment() {
  const [urls, setUrls] = useState('')
  const [platform, setPlatform] = useState('xiaohongshu')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    const list = urls.split('\n').map((s) => s.trim()).filter(Boolean)
    if (list.length === 0) return alert('请输入至少一个博主 URL')
    setLoading(true); setResult(null)
    try {
      setResult(await suggestComments({ blogger_urls: list, platform }))
    } catch (e) {
      alert(e.response?.data?.detail || '生成失败')
    } finally { setLoading(false) }
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center gap-2">
        <h1 className="text-2xl font-bold">评论区 AI 文案</h1>
        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-yellow-100 text-yellow-700 rounded">
          <ShieldCheck className="w-3 h-3" /> 仅管理员
        </span>
      </div>

      <div className="bg-red-50 border border-red-200 rounded p-3 text-xs text-red-800 flex gap-2">
        <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
        <div>
          <b>风控警告：</b>平台对批量评论敏感度很高，远高于发帖。本系统<b>只生成建议文案、不自动发送</b>。
          请人工复制后到目标博主页面手动发布，并控制频率（单账号每小时不超过 3 条）。
        </div>
      </div>

      <div className="bg-white border rounded-lg p-4 space-y-3">
        <div>
          <label className="text-sm text-gray-600 block mb-1">目标平台</label>
          <select value={platform} onChange={(e) => setPlatform(e.target.value)}
            className="border rounded px-3 py-1.5 text-sm">
            <option value="xiaohongshu">小红书</option>
            <option value="douyin">抖音</option>
            <option value="bilibili">B站</option>
            <option value="zhihu">知乎</option>
          </select>
        </div>

        <div>
          <label className="text-sm text-gray-600 block mb-1">博主主页 URL（每行一个）</label>
          <textarea value={urls} onChange={(e) => setUrls(e.target.value)} rows={6}
            placeholder="https://www.xiaohongshu.com/user/...&#10;https://www.xiaohongshu.com/user/..."
            className="w-full border rounded p-2 text-sm font-mono" />
        </div>

        <button onClick={submit} disabled={loading}
          className="bg-brand-600 text-white py-2 px-4 rounded disabled:opacity-50 flex items-center gap-1 text-sm">
          <MessageSquare className="w-4 h-4" />{loading ? '分析中...' : '分析共同点 & 生成评论'}
        </button>
      </div>

      {result && (
        <div className="bg-white border rounded-lg p-4 space-y-4">
          <div>
            <h3 className="font-semibold text-sm mb-1">📊 共同点分析</h3>
            <p className="text-sm text-gray-700">{result.common_analysis}</p>
          </div>

          {result.target_bloggers?.length > 0 && (
            <div>
              <h3 className="font-semibold text-sm mb-1">🎯 推荐投放名单</h3>
              <ul className="space-y-1">
                {result.target_bloggers.map((b, i) => (
                  <li key={i} className="text-sm text-gray-700">
                    <b>{b.name}</b> — {b.reason}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div>
            <h3 className="font-semibold text-sm mb-2">💬 评论文案（3 种风格）</h3>
            <div className="space-y-2">
              {result.comments?.map((c, i) => (
                <CommentCard key={i} style={c.style} text={c.text} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function CommentCard({ style, text }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1500)
  }
  return (
    <div className="p-3 border rounded bg-gray-50">
      <div className="flex justify-between items-start gap-2 mb-1">
        <span className="text-xs font-medium text-brand-600">{style}</span>
        <button onClick={copy} className="text-xs text-gray-500 hover:text-brand-600 flex items-center gap-1">
          <Copy className="w-3 h-3" />{copied ? '已复制' : '复制'}
        </button>
      </div>
      <p className="text-sm">{text}</p>
    </div>
  )
}
