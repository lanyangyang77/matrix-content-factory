"use client"

import { useState, useEffect, FormEvent } from "react"

const STYLE_OPTIONS = [
  { value: "专业型", label: "专业型" },
  { value: "幽默型", label: "幽默型" },
  { value: "情感型", label: "情感型" },
  { value: "干货型", label: "干货型" },
  { value: "故事型", label: "故事型" },
  { value: "猎奇型", label: "猎奇型" },
]

const PLATFORM_OPTIONS = [
  { value: "抖音", label: "抖音", emoji: "🎵" },
  { value: "小红书", label: "小红书", emoji: "📕" },
  { value: "微信公众号", label: "微信公众号", emoji: "💬" },
  { value: "快手", label: "快手", emoji: "🎬" },
  { value: "B站", label: "B站", emoji: "🟦" },
]

interface ContentFormProps {
  onGenerate: (data: { industry: string; style: string; platforms: string[]; audience: string }) => void
  merchantId?: string
  onMerchantChange?: (id: string) => void
  merchants?: { id: string; merchant_name: string; industry: string; target_audience?: string }[]
  loading: boolean
}

export default function ContentForm({
  onGenerate,
  merchantId,
  onMerchantChange,
  merchants = [],
  loading,
}: ContentFormProps) {
  const [industry, setIndustry] = useState("")
  const [audience, setAudience] = useState("")
  const [style, setStyle] = useState("专业型")
  const [platforms, setPlatforms] = useState<string[]>(["抖音", "小红书"])

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"

  useEffect(() => {
    if (!merchantId) return
    const m = merchants.find(x => x.id === merchantId)
    if (m) setIndustry(m.industry)
    fetch(API_BASE + "/api/v1/merchants/" + merchantId)
      .then(r => r.json())
      .then(body => { if (body.success && body.data?.target_audience) setAudience(body.data.target_audience) })
      .catch(() => {})
  }, [merchantId])

  const togglePlatform = (value: string) => {
    setPlatforms((prev) =>
      prev.includes(value) ? prev.filter((p) => p !== value) : [...prev, value]
    )
  }

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!industry.trim()) return
    onGenerate({ industry: industry.trim(), style, platforms, audience: audience.trim() })
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-5">
      <div className="space-y-4">
        {merchants.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">选择商家（可选）</label>
            <select value={merchantId || ""} onChange={(e) => onMerchantChange?.(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500">
              <option value="">不关联商家（通用内容）</option>
              {merchants.map(m => <option key={m.id} value={m.id}>{m.merchant_name}（{m.industry}）</option>)}
            </select>
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">所属行业 <span className="text-red-500">*</span></label>
          <input type="text" value={industry} onChange={(e) => setIndustry(e.target.value)}
            placeholder="例如：新能源汽车、美妆护肤、本地餐饮、家装建材..."
            className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500" required />
          <p className="text-xs text-gray-400 mt-1">输入你所在的行业或产品领域</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">目标受众</label>
          <input type="text" value={audience} onChange={(e) => setAudience(e.target.value)}
            placeholder="例如：25-40岁女性、本地社区居民、企业白领..."
            className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500" />
          <p className="text-xs text-gray-400 mt-1">描述你的目标客户群体（可选）</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">内容风格</label>
          <select value={style} onChange={(e) => setStyle(e.target.value)}
            className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500">
            {STYLE_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">目标平台</label>
          <div className="flex flex-wrap gap-2">
            {PLATFORM_OPTIONS.map(p => (
              <button key={p.value} type="button" onClick={() => togglePlatform(p.value)}
                className={"px-4 py-2 rounded-lg text-sm font-medium border transition-all " +
                  (platforms.includes(p.value) ? "bg-blue-50 border-blue-300 text-blue-700 shadow-sm" : "bg-white border-gray-200 text-gray-600")}>
                <span className="mr-1">{p.emoji}</span>{p.label}
              </button>
            ))}
          </div>
          {platforms.length === 0 && <p className="text-xs text-red-400 mt-1">请至少选择一个目标平台</p>}
        </div>
      </div>
      <button type="submit" disabled={loading || !industry.trim() || platforms.length === 0}
        className="w-full py-3 px-6 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg text-sm font-medium
          hover:from-blue-700 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md">
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            AI 正在拼命中...
          </span>
        ) : "🚀 一键生成内容"}
      </button>
    </form>
  )
}
