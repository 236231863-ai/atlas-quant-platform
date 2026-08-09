// 页面2：我的票（首页，票列表）
const api = require('../../utils/api')

Page({
  data: {
    tickets: [],
    loading: true,
  },

  onShow() {
    this.load()
  },

  async load() {
    const app = getApp()
    if (!app.isAuthed()) {
      wx.navigateTo({ url: '/pages/onboarding/index' })
      return
    }
    try {
      const tickets = await api.listTickets(app.globalData.user_id)
      this.setData({ tickets: tickets || [], loading: false })
    } catch (e) {
      this.setData({ loading: false, tickets: [] })
    }
  },

  add() {
    wx.navigateTo({ url: '/pages/ticket_entry/index' })
  },

  check(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/draw_result/index?ticket_id=${id}` })
  },

  goStats() {
    wx.navigateTo({ url: '/pages/monthly_stats/index' })
  },
})
