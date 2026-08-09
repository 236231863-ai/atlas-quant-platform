// 页面5：提醒设置页（订阅消息授权 + 创建开奖提醒）
const api = require('../../utils/api')

Page({
  data: {
    enabled: false,
    remind_at: '',
    loading: false,
  },

  onLoad() {
    const app = getApp()
    const tickets = wx.getStorageSync('pending_reminder_ticket') || null
    this.setData({ remind_at: tickets ? tickets.draw_date : '' })
  },

  async enable() {
    if (this.data.loading) return
    const app = getApp()
    if (!app.isAuthed()) return
    this.setData({ loading: true })
    try {
      // 请求订阅消息授权（真实模板 id；验证阶段 mock 通过）
      await wx.requestSubscribeMessage({ tmplIds: ['ATLAS_DRAW_TMPL'] }).catch(() => null)
      const pending = wx.getStorageSync('pending_reminder_ticket') || null
      if (pending) {
        await api.createReminder(app.globalData.user_id, pending.ticket_id, pending.issue, pending.draw_date)
      }
      api.track('mobile_reminder_enabled', app.globalData.user_id, {})
      this.setData({ enabled: true, loading: false })
      wx.showToast({ title: '已开启开奖提醒', icon: 'success' })
      wx.navigateTo({ url: '/pages/monthly_stats/index' })
    } catch (e) {
      this.setData({ loading: false })
      wx.showToast({ title: '开启失败', icon: 'none' })
    }
  },
})
