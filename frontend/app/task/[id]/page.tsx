export async function generateStaticParams() { return [{ id: "default" }] }

import { useEffect, useState } from "react"
import Link from "next/link"
import ResultPanel from "@/components/ResultPanel"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"

interface GenerateResult {
  industry: string
  style: string
  platforms: string[]
  angles: { title: string; hook: string; angle_description: string }[]
  posts: { platform: string; title: string; body: string; tags: string[]; visual_suggestion: string }[]
}

export default function TaskPage({ params }: { params: { id: string } }) {
  const taskId = params.id
  const [loading, setLoading] = useState(true)
  const [result, setResult] = useState<GenerateResult | null>(null)
  const [packageId, setPackageId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<string>("查询中...")

  useEffect(() => {
    let cancelled = false
    const poll = async () => {
      while (!cancelled) {
        try {
          const res = await fetch(`${API_BASE}/api/v1/content/task/${taskId}`)
          const body = await res.json()
          if (cancelled) return
          if (body.success && body.data) {
            setStatus(body.data.status === "completed" ? "已完成" : body.data.status === "failed" ? "失败" : "处理中...")
            if (body.data.package_id) setPackageId(body.data.package_id)
            if (body.data.status === "completed") {
              setResult(body.data.result)
              setLoading(false)
              return
            } else if (body.data.status === "failed") {
              setError(body.data.error || "内容生成失败")
              setLoading(false)
              return
            }
          }
        } catch {
          if (!cancelled) {
            setError("无法连接到服务器")
            setLoading(false)
            return
          }
        }
        await new Promise((r) => setTimeout(r, 2000))
      }
    }
    poll()
    return () => { cancelled = true }
  }, [taskId])

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <header className="border-b border-gray-100 bg-white/80 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-3">
          <Link href="/" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
            ← 返回首页
          </Link>
          <div className="text-sm text-gray-500">
            任务状态：<span className="font-medium text-gray-700">{status}</span>
          </div>
        </div>
      </header>
      <main className="max-w-3xl mx-auto px-4 py-8">
        <ResultPanel loading={loading} taskId={taskId} error={error} result={result} />
        {taskId && !result && !error && (
          <div className="mt-4 text-center text-xs text-gray-400">
            <p>任务 ID：{taskId}</p>
            <p className="mt-1">页面每 2 秒自动刷新，无需手动刷新</p>
          </div>
        )}
      </main>
    </div>
  )
}
        <ResultPanel loading={loading} taskId={taskId} packageId={packageId} error={error} result={result} />
