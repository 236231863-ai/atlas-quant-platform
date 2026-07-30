import ReactECharts from "echarts-for-react"
export default function DataAnalysis() {
  const freqOption = {
    title: { text: "Number Frequency (Demo)" },
    xAxis: { type: "category", data: Array.from({length:33},(_,i)=>i+1) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: Array.from({length:33},()=>Math.random()*20), itemStyle: {color:"#5470c6"} }]
  }
  return (
    <div className="page">
      <h1>Data Analysis</h1>
      <div className="chart-container"><ReactECharts option={freqOption} style={{height:400}} /></div>
    </div>
  )
}
