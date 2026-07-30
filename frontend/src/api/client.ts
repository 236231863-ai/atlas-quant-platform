const API_BASE = "/api/v1"
export async function get(path: string) {
  const r = await fetch(`${API_BASE}${path}`)
  if (!r.ok) throw new Error(`API: ${r.status}`)
  return r.json()
}
export async function getDraws(lottery: string, limit = 50) { return get(`/${lottery}/draws?limit=${limit}`) }
export async function getLatest(lottery: string) { return get(`/${lottery}/latest`) }
export async function getStats(lottery: string) { return get(`/${lottery}/statistics`) }
export async function getDashboard() { return get("/dashboard/summary") }
