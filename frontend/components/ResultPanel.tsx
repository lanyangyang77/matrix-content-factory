"use client"

import { useState } from "react"

interface ViralAngle {
  title: string; hook: string; angle_description: string
}

interface PlatformPost {
  platform: string; title: string; body: string; tags: string[]; visual_suggestion: string
}

interface GenerateResult {
  industry: string; style: string; platforms: string[]
  angles: ViralAngle[]; posts: PlatformPost[]
}

interface ResultPanelProps {
  loading: boolean; taskId: string | null; packageId: string | null
  error: string | null; result: GenerateResult | null
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"

const PLATFORM_EMOJI: Record<string, string> = {
  "抖音": "🎵", "小红书": "📕", "微信公众号": "💬", "快手": "🎬", "B站": "🟦",
}
const PLATFORM_COLORS: Record<string, string> = {
  "抖音": "bg-black text-white", "小红书": "bg-red-50 text-red-700 border-red-200",
  "微信公众号": "bg-green-50 text-green-700 border-green-200",
  "快手": "bg-yellow-50 text-yellow-700 border-yellow-200", "B站": "bg-blue-50 text-blue-700 border-blue-200",
}

function LoadingBar() {
  return (
    <div className="bg-white border border-gray-100 rounded-xl p-8 text-center">
      <div className="flex items-center justify-center gap-3 mb-5">
        <svg className="animate-spin h-6 w-6 text-blue-600" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span className="text-base font-medium text-gray-700">AI 正在拼命撰写中，请稍候...</span>
      </div>
      <div className="w-full max-w-md mx-auto bg-gray-100 rounded-full h-2.5 overflow-hidden">
        <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 h-full rounded-full animate-pulse" style={{width: "65%"}}></div>
      </div>
      <p className="text-xs text-gray-400 mt-4">正在分析行业数据，生成爆款角度和平台内容...</p>
    </div>
  )
}

export default function ResultPanel({ loading, taskId, packageId, error, result }: ResultPanelProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const handleCopy = async (post: PlatformPost, idx: number) => {
    const text = `【${post.platform}】${post.title}\n\n${post.body}\n\n${post.tags.map(t => t.startsWith("#") ? t : "#" + t).join(" ")}\n\n🎨 配图建议：${post.visual_suggestion}`
    try {
      await navigator.clipboard.writeText(text)
      setCopiedId("post-" + idx)
      setTimeout(() => setCopiedId(null), 2000)
    } catch { /* ignore */ }
  }

  if (loading) return <div className="mt-8"><LoadingBar /></div>

  if (error) return (
    <div className="mt-8 p-6 bg-red-50 border border-red-200 rounded-xl">
      <div className="flex items-start gap-3"><span className="text-xl">⚠️</span>
        <div><h3 className="font-medium text-red-800">生成失败</h3><p className="text-sm text-red-600 mt-1">{error}</p></div>
      </div>
    </div>
  )

  if (taskId && !result) return (
    <div className="mt-8 p-6 bg-gray-50 border border-gray-200 rounded-xl text-center">
      <div className="flex items-center justify-center gap-2 text-gray-500">
        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span className="text-sm">任务已提交，正在等待 AI 生成...</span>
      </div>
      <p className="text-xs text-gray-400 mt-2">任务 ID：{taskId}</p>
    </div>
  )

  if (!result) return null

  return (
    <div className="mt-8 space-y-8">
      {/* 头部 + 导出按钮 */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-gray-900">✨ 生成结果</h2>
          <p className="text-sm text-gray-500 mt-1">行业：{result.industry} ｜ 风格：{result.style} ｜ 平台：{result.platforms.join("、")}</p>
        </div>
        {packageId && (
          <div className="flex gap-2 shrink-0">
            <a href={`${API_BASE}/api/v1/content/export/${packageId}?format=md`} download
              className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm font-medium hover:bg-green-100 transition shadow-sm">
              📄 下载为 Markdown 资料
            </a>
            <a href={`${API_BASE}/api/v1/content/export/${packageId}?format=xlsx`} download
              className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-purple-50 border border-purple-200 text-purple-700 rounded-lg text-sm font-medium hover:bg-purple-100 transition shadow-sm">
              📊 下载为 Excel 交付包
            </a>
          </div>
        )}
      </div>

      {/* 爆款角度 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-4">💡 爆款切入点</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {result.angles.map((angle, i) => (
            <div key={i} className="bg-gradient-to-br from-yellow-50 to-orange-50 border border-yellow-200 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2">
                <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-orange-400 text-white text-xs font-bold">{i + 1}</span>
                <span className="text-xs text-orange-500 font-medium">爆款角度</span>
              </div>
              <h4 className="font-bold text-gray-900 mb-2">{angle.title}</h4>
              <p className="text-sm text-orange-700 bg-orange-100/50 rounded-lg px-3 py-2 mb-2 italic">「{angle.hook}」</p>
              <p className="text-xs text-gray-600">{angle.angle_description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 各平台内容 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-4">📝 各平台内容</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {result.posts.map((post, i) => (
            <div key={i} className="bg-white border border-gray-100 rounded-xl shadow-sm overflow-hidden flex flex-col">
              <div className={`px-5 py-3 border-b ${PLATFORM_COLORS[post.platform] || "bg-gray-50"}`}>
                <div className="flex items-center gap-2">
                  <span className="text-lg">{PLATFORM_EMOJI[post.platform] || "📱"}</span>
                  <span className="font-semibold text-sm">{post.platform}</span>
                </div>
              </div>
              <div className="p-5 space-y-4 flex-1 flex flex-col">
                <div>
                  <span className="text-xs text-gray-400 uppercase tracking-wide">标题</span>
                  <h4 className="font-bold text-gray-900 text-base mt-1">{post.title}</h4>
                </div>
                <div className="flex-1">
                  <span className="text-xs text-gray-400 uppercase tracking-wide">正文</span>
                  <div className="mt-1 text-sm text-gray-700 leading-relaxed whitespace-pre-wrap line-clamp-6">{post.body}</div>
                </div>
                <div>
                  <span className="text-xs text-gray-400 uppercase tracking-wide">话题标签</span>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {post.tags.map((tag, ti) => (
                      <span key={ti} className="inline-block px-2.5 py-1 bg-blue-50 text-blue-600 rounded-full text-xs font-medium">
                        {tag.startsWith("#") ? tag : "#" + tag}
                      </span>
                    ))}
                  </div>
                </div>
                {post.visual_suggestion && (
                  <div className="bg-purple-50 border border-purple-100 rounded-lg p-3">
                    <span className="text-xs text-purple-500 font-medium">🎨 画面建议</span>
                    <p className="text-sm text-purple-700 mt-1">{post.visual_suggestion}</p>
                  </div>
                )}
                {/* 一键复制按钮 */}
                <button onClick={() => handleCopy(post, i)}
                  className="mt-auto w-full py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition active:scale-[0.98]">
                  {copiedId === "post-" + i ? "✅ 已复制到剪贴板" : "📋 一键复制全文"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
