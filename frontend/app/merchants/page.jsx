"use client"
import { useState, useEffect } from "react"
export const dynamic = "force-dynamic"


export default function MerchantsPage() {
  const [merchants, setMerchants] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState(null)
  const [form, setForm] = useState({ merchant_name: "", industry: "", target_audience: "", notes: "" })
  const [history, setHistory] = useState(null)
  const [historyLoading, setHistoryLoading] = useState(false)

  const fetchMerchants = async () => {
    try {
      const res = await fetch(API_BASE + "/api/v1/merchants")
      const body = await res.json()
      if (body.success) setMerchants(body.data || [])
    } catch (e) { }
    setLoading(false)
  }

  useEffect(() => { fetchMerchants() }, [])

  const saveMerchant = async () => {
    if (!form.merchant_name.trim()) return
    try {
      const method = editId ? "PUT" : "POST"
      const url = editId ? API_BASE + "/api/v1/merchants/" + editId : API_BASE + "/api/v1/merchants"
      await fetch(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) })
      setShowForm(false); setEditId(null); setForm({ merchant_name: "", industry: "", target_audience: "", notes: "" })
      fetchMerchants()
    } catch (e) { }
  }

  const deleteMerchant = async (id) => {
    if (!confirm("确定删除？")) return
    try { await fetch(API_BASE + "/api/v1/merchants/" + id, { method: "DELETE" }); fetchMerchants() }
    catch (e) { }
  }

  const showHistory = async (m) => {
    setHistoryLoading(true); setHistory({ merchantId: m.id, merchantName: m.merchant_name, items: [] })
    try {
      const res = await fetch(API_BASE + "/api/v1/merchants/" + m.id + "/content")
      const body = await res.json()
      if (body.success) setHistory({ merchantId: m.id, merchantName: m.merchant_name, items: body.data || [] })
    } catch (e) { }
    setHistoryLoading(false)
  }

  const edit = (m) => {
    setForm({ merchant_name: m.merchant_name, industry: m.industry, target_audience: m.target_audience || "", notes: m.notes || "" })
    setEditId(m.id); setShowForm(true)
  }

  if (loading) return <div className="p-6 text-center text-gray-400 text-sm py-12">加载中...</div>

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🏪 商家管理</h2>
          <p className="text-sm text-gray-500 mt-1">管理客户商家档案</p>
        </div>
        <button onClick={() => { setShowForm(true); setEditId(null); setForm({ merchant_name: "", industry: "", target_audience: "", notes: "" }) }}
          className="px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition shadow-sm">+ 新增商家</button>
      </div>

      {showForm && (
        <div className="bg-white border rounded-xl p-5 mb-6 space-y-4">
          <input type="text" value={form.merchant_name} onChange={e => setForm({ ...form, merchant_name: e.target.value })}
            placeholder="商家名称 *" className="w-full px-3 py-2 border rounded-lg text-sm" />
          <input type="text" value={form.industry} onChange={e => setForm({ ...form, industry: e.target.value })}
            placeholder="所属行业 *" className="w-full px-3 py-2 border rounded-lg text-sm" />
          <input type="text" value={form.target_audience} onChange={e => setForm({ ...form, target_audience: e.target.value })}
            placeholder="目标客户群体" className="w-full px-3 py-2 border rounded-lg text-sm" />
          <textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })}
            rows={2} placeholder="备注" className="w-full px-3 py-2 border rounded-lg text-sm" />
          <div className="flex gap-2 justify-end">
            <button onClick={() => { setShowForm(false); setEditId(null) }}
              className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50">取消</button>
            <button onClick={saveMerchant}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">{editId ? "保存" : "创建"}</button>
          </div>
        </div>
      )}

      {!showForm && merchants.length === 0 ? (
        <div className="text-center py-16 bg-white border rounded-xl">
          <div className="text-4xl mb-3">🏪</div>
          <p className="text-gray-500 font-medium">还没有商家档案</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {merchants.map(m => (
            <div key={m.id} className="bg-white border rounded-xl p-5 shadow-sm">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold">{m.merchant_name}</h3>
                  <span className="bg-blue-50 text-blue-600 text-xs px-2 py-0.5 rounded mt-1">{m.industry}</span>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => edit(m)} className="hover:text-blue-600">✏️</button>
                  <button onClick={() => deleteMerchant(m.id)} className="hover:text-red-600">🗑️</button>
                </div>
              </div>
              {m.target_audience && <p className="text-xs text-gray-500 mb-2">目标客户：{m.target_audience}</p>}
              <div className="text-xs text-gray-400 flex gap-3">
                <span>内容：{m.content_count || 0} 条</span>
                <button onClick={() => showHistory(m)} className="text-blue-600 font-medium">查看历史</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {history && (
        <div className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center p-4" onClick={() => setHistory(null)}>
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[70vh] overflow-auto" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between p-5 border-b">
              <h3 className="font-bold">{history.merchantName} - 历史内容</h3>
              <button onClick={() => setHistory(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="p-5 space-y-3">
              {historyLoading ? <div className="py-8 text-center text-gray-400">加载中...</div> :
               history.items.length === 0 ? <div className="py-8 text-center text-gray-400">暂无历史</div> :
               history.items.map(item => (
                <div key={item.id} className="p-4 bg-gray-50 rounded-lg border">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{item.industry} - {item.style}</span>
                    <span className={"text-xs px-2 py-0.5 rounded-full " + (item.status === "completed" ? "bg-green-50 text-green-600" : "bg-yellow-50 text-yellow-600")}>
                      {item.status === "completed" ? "已完成" : item.status === "failed" ? "失败" : "处理中"}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400">平台：{(item.platforms || []).join("、")}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"
