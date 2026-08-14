// 页面4：开奖结果页（核对指定票 → 中奖状态）
const api = require('../../utils/api')

Page({
  data: {
    ticket_id: '',
    issue: '',
    draw_date: '',
    result: null,
    loading: true,
  },

  onLoad(query) {
    this.setData({ ticket_id: query.ticket_id || '' })
    this.check()
  },

  async check() {
    const app = getApp()
    if (!app.isAuthed()) return
    this.setData({ loading: true })
    try {
      // 用最新开奖核对（验证阶段取最新期）
      const latest = await api.latestDraw('dlt')
      const issue = latest.issue
      const draw_date = latest.draw_date || ''
      const res = await api.checkDraw(app.globalData.user_id, this.data.ticket_id, issue)
      api.track('mobile_draw_viewed', app.globalData.user_id, { ticket_id: this.data.ticket_id, issue })
      this.setData({ issue, draw_date, result: res.result, loading: false })
    } catch (e) {
      this.setData({ loading: false, result: null })
    }
  },

  goStats() {
    wx.navigateTo({ url: '/pages/monthly_stats/index' })
  },

  goReminder() {
    wx.setStorageSync('pending_reminder_ticket', {
      ticket_id: this.data.ticket_id,
      issue: this.data.issue,
      draw_date: this.data.draw_date || '',
    })
    wx.navigateTo({ url: '/pages/reminder_setting/index' })
  },

  goHome() {
    wx.navigateTo({ url: '/pages/my_tickets/index' })
  },
})
