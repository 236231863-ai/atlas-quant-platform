// Atlas Mobile MVP - API 客户端（极简，POST/GET + 埋点上报）

// 真机预览：指向电脑局域网 IP（手机与电脑同一 WiFi）
// 正式部署：替换为 HTTPS 域名
const BASE = 'http://192.168.31.95:8000/api/mobile/v1'

function request(path, method, data) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: BASE + path,
      method,
      data,
      success: (res) => resolve(res.data),
      fail: (err) => reject(err),
    })
  })
}

// 埋点上报（source=MOBILE）
function track(event_name, user_id, metadata) {
  return request('/events', 'POST', {
    event_name, user_id, source: 'MOBILE', metadata: metadata || {},
  }).catch(() => null)
}

// 真实微信登录（wx.login code → 后端 code2session → openid → U_ID）
// 注意：auth 路由前缀是 /api/auth（与 mobile 路由分开）
const AUTH_BASE = BASE.replace('/api/mobile/v1', '/api/auth')
function wechatLogin(code, lottery_type, purchase_frequency) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: AUTH_BASE + '/wechat/login',
      method: 'POST',
      data: { code, lottery_type, purchase_frequency },
      success: (res) => resolve(res.data),
      fail: (err) => reject(err),
    })
  })
}

module.exports = {
  auth: (openid, lottery_type, purchase_frequency) =>
    request('/users/auth', 'POST', { openid, lottery_type, purchase_frequency }),
  wechatLogin,
  saveTicket: (user_id, lottery, text, buy_date, draw_date) =>
    request('/tickets', 'POST', { user_id, lottery, text, buy_date, draw_date }),
  listTickets: (user_id) => request(`/tickets?user_id=${user_id}`, 'GET'),
  checkDraw: (user_id, ticket_id, issue) =>
    request('/draws/check', 'POST', { user_id, ticket_id, issue }),
  latestDraw: (lottery) => request(`/draws/latest?lottery=${lottery}`, 'GET'),
  createReminder: (user_id, ticket_id, issue, remind_at) =>
    request('/reminders', 'POST', { user_id, ticket_id, issue, remind_at }),
  reminderClick: (reminder_id) =>
    request('/reminders/click', 'POST', { reminder_id }),
  track,
}
