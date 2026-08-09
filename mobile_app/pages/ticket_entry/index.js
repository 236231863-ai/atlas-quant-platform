// 页面3：录票页（核心入口：粘贴号码 → 保存 → 跳开奖结果）
const api = require('../../utils/api')

Page({
  data: {
    lottery: 'dlt',
    text: '',
    saving: false,
    hint: '',
  },

  onLotteryChange(e) {
    this.setData({ lottery: e.detail.value })
  },

  onInput(e) {
    this.setData({ text: e.detail.value })
  },

  async save() {
    if (this.data.saving) return
    const app = getApp()
    if (!app.isAuthed()) {
      wx.navigateTo({ url: '/pages/onboarding/index' })
      return
    }
    const text = this.data.text.trim()
    if (!text) {
      this.setData({ hint: '请输入号码' })
      return
    }
    this.setData({ saving: true, hint: '' })
    try {
      const result = await api.saveTicket(app.globalData.user_id, this.data.lottery, text)
      api.track('mobile_ticket_saved', app.globalData.user_id, { ticket_id: result.ticket_id })
      wx.showToast({ title: '已保存', icon: 'success' })
      wx.navigateTo({
        url: `/pages/draw_result/index?ticket_id=${result.ticket_id}`,
      })
    } catch (e) {
      this.setData({ hint: (e && e.message) || '号码格式错误，请检查' })
    } finally {
      this.setData({ saving: false })
    }
  },
})
