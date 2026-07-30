const API="/api/product"
export async function get(path){const r=await fetch(`${API}${path}`);if(!r.ok)throw new Error(`API:${r.status}`);return r.json()}
export async function post(path,body){const r=await fetch(`${API}${path}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});if(!r.ok)throw new Error(`API:${r.status}`);return r.json()}
export function getDashboard(){return get("/dashboard")}
export function analyze(req){return post("/analyze",req)}
export function getReport(id){return get(`/report/${id}`)}
export function getHistory(){return get("/history")}
