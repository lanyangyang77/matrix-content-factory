"use client"

import { usePathname } from "next/navigation"
import Link from "next/link"
import "./globals.css"

const NAV_ITEMS = [
  { href: "/", label: "内容生成", icon: "🚀" },
  { href: "/merchants", label: "商家管理", icon: "🏪" },
]

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js")
    }
  }, [])

  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-gray-50 flex">
        {/* 侧边栏 */}
        <aside className="w-56 bg-white border-r border-gray-100 flex flex-col shrink-0">
          {/* 品牌 */}
          <div className="px-5 py-5 border-b border-gray-100">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-xs shadow-md shrink-0">
                M
              </div>
              <div>
                <h1 className="text-sm font-bold text-gray-900">矩阵内容工厂</h1>
                <p className="text-[10px] text-gray-400">智能内容生成平台</p>
              </div>
            </div>
          </div>

          {/* 导航 */}
          <nav className="flex-1 px-3 py-4 space-y-1">
            {NAV_ITEMS.map((item) => {
              const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href))
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                    active
                      ? "bg-blue-50 text-blue-700 font-medium shadow-sm"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-800"
                  }`}
                >
                  <span className="text-base">{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>

          {/* 底部 */}
          <div className="px-5 py-4 border-t border-gray-100">
            <p className="text-[10px] text-gray-300">© 2026 矩阵内容工厂</p>
          </div>
        </aside>

        {/* 主内容 */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </body>
    </html>
  )
}
import { useEffect } from "react"
    const link = document.createElement("link")
    link.rel = "manifest"
    link.href = "/manifest.json"
    document.head.appendChild(link)
    const meta = document.createElement("meta")
    meta.name = "theme-color"
    meta.content = "#2563eb"
    document.head.appendChild(meta)
