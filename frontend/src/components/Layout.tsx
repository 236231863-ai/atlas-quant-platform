import { NavLink } from "react-router-dom"
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="layout">
      <nav className="sidebar">
        <h2>Atlas Quant</h2>
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/analysis">Data Analysis</NavLink>
        <NavLink to="/strategies">Strategy Lab</NavLink>
        <NavLink to="/backtest">Backtest Center</NavLink>
        <NavLink to="/ai">AI Assistant</NavLink>
        <NavLink to="/reports">Reports</NavLink>
      </nav>
      <main className="content">{children}</main>
    </div>
  )
}
