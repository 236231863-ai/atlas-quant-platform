import ReactECharts from "echarts-for-react"
export default function BacktestCenter() {
  const roiOption = {
    title: { text: "ROI Curve (Demo)" },
    xAxis: { type: "category", data: Array.from({length:20},(_,i)=>`Draw ${i+1}`) },
    yAxis: { type: "value" },
    series: [{ type: "line", data: Array.from({length:20},()=>Math.random()*10-3), smooth: true, areaStyle: {} }]
  }
  return (
    <div className="page">
      <h1>Backtest Center</h1>
      <div className="chart-container"><ReactECharts option={roiOption} style={{height:400}} /></div>
    </div>
  )
}
