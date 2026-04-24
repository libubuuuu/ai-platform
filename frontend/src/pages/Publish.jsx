import { useEffect, useState } from 'react'
import { Plus, Trash2, Send, ShieldCheck, RefreshCw } from 'lucide-react'
import {
  listAccounts, createAccount, deleteAccount,
  listRewrites, publish, listPublishTasks,
} from '../api'

const PLATFORMS = [
  'douyin', 'xiaohongshu', 'bilibili', 'kuaishou',
  'wechat_channel', 'baijiahao', 'tiktok',
]

export default function Publish() {
  const [accounts, setAccounts] = useState([])
  const [rewrites, setRewrites] = useState([])
  const [tasks, setTasks] = useState([])

  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({
    platform: 'xiaohongshu', display_name: '', cookies: '', proxy_url: '', user_agent: '',
  })

  const [selectedRewrite, setSelectedRewrite] = useState(null)
  const [selectedAccounts, setSelectedAccounts] = useState([])

  const reload = async () => {
    const [a, r, t] = await Promise.all([listAccounts(), listRewrites(), listPublishTasks()])
    setAccounts(a); setRewrites(r); setTasks(t)
  }
  useEffect(() => { reload() }, [])

  const submitAccount = async () => {
    try { await createAccount(form); setShowAdd(false); reload() }
    catch (e) { alert(e.response?.data?.detail || '创建失败') }
  }

  const doPublish = async () => {
    if (!selectedRewrite || selectedAccounts.length === 0)
      return alert('请选择要发布的内容和账号')
    try {
      await publish({
        rewritten_id: selectedRewrite.id,
        account_ids: selectedAccounts,
        target: 'draft',
      })
      alert('已创建发布任务，目标：草稿箱')
      reload()
    } catch (e) {
      alert(e.response?.data?.detail || '发布失败')
    }
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center gap-2">
        <h1 className="text-2xl font-bold">一键发布草稿箱</h1>
        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-yellow-100 text-yellow-700 rounded">
          <ShieldCheck className="w-3 h-3" /> 仅管理员
        </span>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded p-3 text-xs text-amber-800">
        ⚠️ 安全底线：本系统所有发布都只进入<b>草稿箱</b>，不会直接公开。
        最终发布请人工在目标平台的创作后台点击确认。
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* 账号列表 */}
        <div className="bg-white border rounded-lg p-4">
          <div className="flex justify-between items-center mb-3">
            <h2 className="font-semibold text-sm">平台账号矩阵</h2>
            <button onClick={() => setShowAdd(true)}
              className="text-xs flex items-center gap-1 text-brand-600"><Plus className="w-3 h-3" />新增</button>
          </div>

          {accounts.length === 0 && <p className="text-xs text-gray-400">尚未添加账号</p>}
          <div className="space-y-2 max-h-96 overflow-auto">
            {accounts.map((a) => (
              <label key={a.id} className={`flex gap-2 p-2 rounded border cursor-pointer ${selectedAccounts.includes(a.id) ? 'border-brand-500 bg-brand-50' : ''}`}>
                <input type="checkbox" checked={selectedAccounts.includes(a.id)}
                  onChange={() => setSelectedAccounts((s) =>
                    s.includes(a.id) ? s.filter((x) => x !== a.id) : [...s, a.id])} className="mt-1" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium">{a.display_name}</div>
                  <div className="text-xs text-gray-500">{a.platform} {a.proxy_url && `· 🌐 ${a.proxy_url}`}</div>
                </div>
                <button onClick={async (e) => {
                  e.preventDefault()
                  if (confirm(`删除账号 ${a.display_name}?`)) { await deleteAccount(a.id); reload() }
                }} className="p-1 text-gray-400 hover:text-red-500">
                  <Trash2 className="w-3 h-3" />
                </button>
              </label>
            ))}
          </div>

          {showAdd && (
            <div className="mt-3 p-3 border rounded space-y-2 bg-gray-50">
              <select value={form.platform} onChange={(e) => setForm({ ...form, platform: e.target.value })}
                className="w-full text-sm border rounded px-2 py-1">
                {PLATFORMS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
              <input placeholder="账号显示名" value={form.display_name}
                onChange={(e) => setForm({ ...form, display_name: e.target.value })}
                className="w-full text-sm border rounded px-2 py-1" />
              <textarea placeholder="Cookies（可选，建议用扫码登录生成 storage_state）"
                value={form.cookies} rows={2}
                onChange={(e) => setForm({ ...form, cookies: e.target.value })}
                className="w-full text-sm border rounded px-2 py-1 font-mono" />
              <input placeholder="代理 URL（可选，建议每账号独立代理）"
                value={form.proxy_url}
                onChange={(e) => setForm({ ...form, proxy_url: e.target.value })}
                className="w-full text-sm border rounded px-2 py-1" />
              <div className="flex gap-2">
                <button onClick={submitAccount}
                  className="flex-1 bg-brand-600 text-white text-sm py-1 rounded">保存</button>
                <button onClick={() => setShowAdd(false)}
                  className="flex-1 border text-sm py-1 rounded">取消</button>
              </div>
            </div>
          )}
        </div>

        {/* 选择洗稿结果 */}
        <div className="bg-white border rounded-lg p-4">
          <h2 className="font-semibold text-sm mb-3">选择要发布的洗稿内容</h2>
          <div className="space-y-2 max-h-96 overflow-auto">
            {rewrites.map((r) => (
              <div key={r.id} onClick={() => setSelectedRewrite(r)}
                className={`p-2 border rounded cursor-pointer text-sm ${selectedRewrite?.id === r.id ? 'border-brand-500 bg-brand-50' : ''}`}>
                <div className="font-medium truncate">{r.title}</div>
                <div className="text-xs text-gray-500 truncate">{r.content_text}</div>
              </div>
            ))}
          </div>
        </div>

        {/* 发布操作 + 任务列表 */}
        <div className="space-y-3">
          <div className="bg-white border rounded-lg p-4 space-y-3">
            <h2 className="font-semibold text-sm">发布</h2>
            <p className="text-xs text-gray-500">
              已选洗稿：{selectedRewrite ? selectedRewrite.title.slice(0, 20) : '—'}<br />
              已选账号：{selectedAccounts.length} 个
            </p>
            <button onClick={doPublish} disabled={!selectedRewrite || selectedAccounts.length === 0}
              className="w-full bg-brand-600 text-white py-2 rounded disabled:opacity-50 flex items-center justify-center gap-1 text-sm">
              <Send className="w-4 h-4" />一键发布到草稿箱
            </button>
          </div>

          <div className="bg-white border rounded-lg p-4">
            <div className="flex justify-between items-center mb-2">
              <h2 className="font-semibold text-sm">任务记录</h2>
              <button onClick={reload} className="text-gray-400 hover:text-brand-600">
                <RefreshCw className="w-3 h-3" />
              </button>
            </div>
            <div className="space-y-1 max-h-60 overflow-auto text-xs">
              {tasks.slice(0, 20).map((t) => (
                <div key={t.id} className="flex justify-between p-1.5 rounded bg-gray-50">
                  <span>#{t.id} → 账号 {t.account_id}</span>
                  <span className={
                    t.status === 'success' ? 'text-green-600' :
                    t.status === 'failed' ? 'text-red-600' :
                    t.status === 'running' ? 'text-blue-600' : 'text-gray-500'
                  }>{t.status}</span>
                </div>
              ))}
              {tasks.length === 0 && <p className="text-gray-400">无记录</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
