// 页面6：本月统计页（投入 / 中奖 / 净额）
const api = require('../../utils/api')

Page({
  data: {
    total_cost: 0,
    total_win: 0,
    net: 0,
    count: 0,
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
      let total_cost = 0
      let total_win = 0
      for (const t of tickets || []) {
        total_cost += t.cost || 0
        // 中奖金额需核对；验证阶段展示成本 + 票数
      }
      this.setData({
        total_cost,
        total_win,
        net: total_win - total_cost,
        count: (tickets || []).length,
        loading: false,
      })
    } catch (e) {
      this.setData({ loading: false })
    }
  },
})
