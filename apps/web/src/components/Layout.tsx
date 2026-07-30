import {NavLink} from "react-router-dom"
export default function Layout({children}:{children:React.ReactNode}){
return(<div className="layout">
<nav className="sidebar"><h2>Atlas Quant</h2>
<NavLink to="/">Home</NavLink>
<NavLink to="/analysis">Analysis</NavLink>
<NavLink to="/strategy">Strategy</NavLink>
<NavLink to="/history">History</NavLink>
</nav>
<main className="content">{children}</main>
</div>)}
