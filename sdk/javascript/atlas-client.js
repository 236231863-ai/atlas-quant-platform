class AtlasClient {
    constructor(apiKey, baseUrl = "http://localhost:8000/api/v3") { this.apiKey = apiKey; this.baseUrl = baseUrl; }
    async request(method, path, data) {
        const res = await fetch(`${this.baseUrl}${path}`, { method, headers: {"Authorization":`Bearer ${this.apiKey}`,"Content-Type":"application/json"}, body: data ? JSON.stringify(data) : undefined });
        if (!res.ok) throw new Error(`API: ${res.status}`); return res.json();
    }
    async analyze(lottery = "dlt", mode = "basic") { return this.request("POST", "/analyze", {lottery_code: lottery, mode}); }
    async getReport(id) { return this.request("GET", `/report/${id}`); }
}
module.exports = { AtlasClient };
