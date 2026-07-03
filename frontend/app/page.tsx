"use client"

import { useState, useCallback, useRef, useEffect } from "react"
import ContentForm from "@/components/ContentForm"
import ResultPanel from "@/components/ResultPanel"
export const dynamic = "force-dynamic"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"

interface GenerateResult {
  industry: string; style: string; platforms: string[]
  angles: { title: string; hook: string; angle_description: string }[]
  posts: { platform: string; title: string; body: string; tags: string[]; visual_suggestion: string }[]
}

export default function Home() {
  const [loading, setLoading] = useState(false)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [packageId, setPackageId] = useState<string | null>(null)
  const [result, setResult] = useState<GenerateResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [merchants, setMerchants] = useState<{ id: string; merchant_name: string; industry: string }[]>([])
  const [merchantId, setMerchantId] = useState("")
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    fetch(API_BASE + "/api/v1/merchants")
      .then((r) => r.json())
      .then((body) => { if (body.success) setMerchants(body.data || []) })
      .catch(() => {})
  }, [])

  const stopPolling = useCallback(() => {
    if (pollingRef.current) { clearInterval(pollingRef.current); pollingRef.current = null }
  }, [])

  const startPolling = useCallback((id: string) => {
    stopPolling()
    const interval = setInterval(async () => {
      try {
        const res = await fetch(API_BASE + "/api/v1/content/task/" + id)
        const body = await res.json()
        if (body.success && body.data) {
          const st = body.data.status
          if (st === "completed") { setResult(body.data.result); setLoading(false); stopPolling() }
          else if (st === "failed") { setError(body.data.error || "生成失败"); setLoading(false); stopPolling() }
        }
      } catch { }
    }, 3000)
    pollingRef.current = interval
  }, [stopPolling])

  const handleGenerate = async (data: { industry: string; style: string; platforms: string[]; audience: string }) => {
    setLoading(true); setError(null); setResult(null); setTaskId(null); setPackageId(null); stopPolling()
    try {
      const res = await fetch(API_BASE + "/api/v1/content/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, merchant_id: merchantId || undefined }),
      })
      const body = await res.json()
      if (body.success && body.data?.task_id) {
        const id = body.data.task_id
        setTaskId(id)
        if (body.data.package_id) setPackageId(body.data.package_id)
        startPolling(id)
        if (body.data.status === "completed" && body.data.result) {
          setResult(body.data.result)
          if (body.data.package_id) setPackageId(body.data.package_id)
          setLoading(false); stopPolling()
        }
      } else {
        const detail = body.detail || body.message || "请求失败"
        setError(typeof detail === "string" ? detail : "服务暂时不可用")
        setLoading(false)
      }
    } catch { setError("无法连接到服务器"); setLoading(false) }
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-8 text-center">
        <h2 className="text-3xl font-bold text-gray-900">🔥 爆款内容生成器</h2>
        <p className="text-gray-500 mt-2">输入你的行业，AI 自动生成爆款营销内容</p>
      </div>
      <div className="max-w-2xl mx-auto">
        <ContentForm onGenerate={handleGenerate} loading={loading}
          merchants={merchants} merchantId={merchantId} onMerchantChange={setMerchantId} />
      </div>
      <div className="max-w-3xl mx-auto">
        <ResultPanel loading={loading} taskId={taskId} packageId={packageId} error={error} result={result} />
      </div>
      {!taskId && !result && !error && (
        <div className="max-w-2xl mx-auto mt-12 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white border border-gray-100 rounded-xl p-5 text-center">
            <div className="text-2xl mb-2">📝</div>
            <h4 className="font-semibold text-gray-800 text-sm">输入行业</h4>
            <p className="text-xs text-gray-400 mt-1">填写你所在的行业或产品类目</p>
          </div>
          <div className="bg-white border border-gray-100 rounded-xl p-5 text-center">
            <div className="text-2xl mb-2">🤖</div>
            <h4 className="font-semibold text-gray-800 text-sm">AI 创作</h4>
            <p className="text-xs text-gray-400 mt-1">智能生成爆款角度和文案</p>
          </div>
          <div className="bg-white border border-gray-100 rounded-xl p-5 text-center">
            <div className="text-2xl mb-2">🚀</div>
            <h4 className="font-semibold text-gray-800 text-sm">多平台发布</h4>
            <p className="text-xs text-gray-400 mt-1">导出适合各平台的内容</p>
          </div>
        </div>
      )}
    </div>
  )
}
