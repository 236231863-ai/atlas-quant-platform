import { Routes, Route } from "react-router-dom"
import Layout from "./components/Layout"
import Dashboard from "./pages/Dashboard"
import DataAnalysis from "./pages/DataAnalysis"
import StrategyLab from "./pages/StrategyLab"
import BacktestCenter from "./pages/BacktestCenter"
import AIAssistant from "./pages/AIAssistant"
import ReportViewer from "./pages/ReportViewer"
export default function App() {
  return (<Layout><Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/analysis" element={<DataAnalysis />} />
    <Route path="/strategies" element={<StrategyLab />} />
    <Route path="/backtest" element={<BacktestCenter />} />
    <Route path="/ai" element={<AIAssistant />} />
    <Route path="/reports" element={<ReportViewer />} />
  </Routes></Layout>)
}
