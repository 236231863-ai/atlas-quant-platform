// Atlas Mobile MVP - API 客户端（极简，POST/GET + 埋点上报）

const BASE = 'http://127.0.0.1:8000/api/mobile/v1'

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

module.exports = {
  auth: (openid, lottery_type, purchase_frequency) =>
    request('/users/auth', 'POST', { openid, lottery_type, purchase_frequency }),
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
