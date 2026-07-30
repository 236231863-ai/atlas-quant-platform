import {Routes,Route} from "react-router-dom"
import Layout from "./components/Layout"
import Home from "./pages/Home";import Analysis from "./pages/Analysis";import Strategy from "./pages/Strategy"
import Report from "./pages/Report";import History from "./pages/History"
export default function App(){return(<Layout><Routes>
<Route path="/" element={<Home/>}/>
<Route path="/analysis" element={<Analysis/>}/>
<Route path="/strategy" element={<Strategy/>}/>
<Route path="/report/:id" element={<Report/>}/>
<Route path="/history" element={<History/>}/>
</Routes></Layout>)}
