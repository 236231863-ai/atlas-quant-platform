import { useEffect, useState } from "react"
import { getDashboard } from "../api/client"

export default function Dashboard() {
  const [data, setData] = useState<any>(null)
  useEffect(() => { getDashboard().then(setData).catch(() => {}) }, [])
  return (
    <div className="page">
      <h1>Dashboard</h1>
      <div className="cards">
        <div className="card"><h3>Total Games</h3><div className="value">{data?.total_games ?? "-"}</div></div>
        <div className="card"><h3>Status</h3><div className="value" style={{fontSize:16}}>System Online</div></div>
        <div className="card"><h3>Version</h3><div className="value" style={{fontSize:16}}>v0.7.0</div></div>
      </div>
    </div>
  )
}
