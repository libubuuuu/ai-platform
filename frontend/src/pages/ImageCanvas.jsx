import { useState, useRef } from 'react'
import { Upload, Wand2, RotateCcw } from 'lucide-react'
import { extractPrompt, generateImages } from '../api'

export default function ImageCanvas() {
  const [refImage, setRefImage] = useState(null)
  const [prompt, setPrompt] = useState('')
  const [count, setCount] = useState(4)
  const [generated, setGenerated] = useState([])
  const [loading, setLoading] = useState(false)
  const [stage, setStage] = useState('upload') // upload | prompt | generated
  const fileInput = useRef()

  const onUpload = (f) => {
    if (!f) return
    const reader = new FileReader()
    reader.onload = () => { setRefImage(reader.result); setStage('prompt') }
    reader.readAsDataURL(f)
  }

  const doExtract = async () => {
    if (!refImage) return
    setLoading(true)
    try {
      const { prompt } = await extractPrompt(refImage)
      setPrompt(prompt)
    } catch (e) {
      alert(e.response?.data?.detail || '抽取失败')
    } finally { setLoading(false) }
  }

  const doGenerate = async () => {
    if (!prompt) return alert('请先输入或抽取提示词')
    setLoading(true)
    try {
      const { images } = await generateImages({ prompt, count, reference_image: refImage })
      setGenerated(images); setStage('generated')
    } catch (e) {
      alert(e.response?.data?.detail || '生成失败。请确认 ComfyUI 已部署且 COMFYUI_ENABLED=true')
    } finally { setLoading(false) }
  }

  const regenerateFrom = (imgUrl) => {
    setRefImage(imgUrl); setStage('prompt'); setGenerated([])
  }

  const reset = () => {
    setRefImage(null); setPrompt(''); setGenerated([]); setStage('upload')
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">图片画布 · AI 相似图生成</h1>
        <button onClick={reset} className="flex items-center gap-1 text-sm text-gray-500 hover:text-brand-600">
          <RotateCcw className="w-4 h-4" /> 重置
        </button>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded p-3 text-xs text-amber-800">
        ⚠️ 此功能依赖本地 ComfyUI 服务。如未部署，请先按 README 指引安装 ComfyUI，然后在 <code>.env</code> 中设置 <code>COMFYUI_ENABLED=true</code>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 1. 上传 */}
        <div className="bg-white border rounded-lg p-4">
          <h2 className="font-semibold text-sm mb-3">① 上传参考图</h2>
          {refImage ? (
            <img src={refImage} alt="" className="w-full aspect-square object-cover rounded" />
          ) : (
            <div
              onClick={() => fileInput.current?.click()}
              className="aspect-square border-2 border-dashed rounded flex items-center justify-center cursor-pointer hover:border-brand-500"
            >
              <div className="text-center text-gray-400">
                <Upload className="w-8 h-8 mx-auto mb-2" />
                <p className="text-sm">点击上传图片</p>
              </div>
            </div>
          )}
          <input type="file" ref={fileInput} onChange={(e) => onUpload(e.target.files?.[0])}
            accept="image/*" className="hidden" />
        </div>

        {/* 2. 提示词 */}
        <div className="bg-white border rounded-lg p-4">
          <h2 className="font-semibold text-sm mb-3">② 提示词</h2>
          <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)}
            placeholder="描述图片特征..." rows={5}
            className="w-full border rounded p-2 text-sm resize-none" />
          <div className="flex gap-2 mt-2">
            <button onClick={doExtract} disabled={!refImage || loading}
              className="flex-1 text-xs py-2 border rounded disabled:opacity-50">抽取提示词</button>
          </div>
          <div className="mt-3">
            <label className="text-xs text-gray-600">生成数量：{count}</label>
            <input type="range" min={1} max={8} value={count}
              onChange={(e) => setCount(Number(e.target.value))} className="w-full" />
          </div>
          <button onClick={doGenerate} disabled={!prompt || loading}
            className="w-full mt-2 bg-brand-600 text-white py-2 rounded disabled:opacity-50 flex items-center justify-center gap-1 text-sm">
            <Wand2 className="w-4 h-4" />{loading ? '生成中...' : '生成相似图'}
          </button>
        </div>

        {/* 3. 结果 */}
        <div className="bg-white border rounded-lg p-4">
          <h2 className="font-semibold text-sm mb-3">③ 生成结果</h2>
          {generated.length === 0 ? (
            <p className="text-xs text-gray-400">尚未生成</p>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              {generated.map((url, i) => (
                <div key={i} className="relative group">
                  <img src={url} alt="" className="w-full aspect-square object-cover rounded" />
                  <button onClick={() => regenerateFrom(url)}
                    className="absolute inset-0 bg-black/60 text-white text-xs opacity-0 group-hover:opacity-100 transition rounded flex items-center justify-center">
                    以此为参考再生成
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
