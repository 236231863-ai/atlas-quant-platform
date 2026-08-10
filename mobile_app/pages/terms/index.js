// 首次使用协议页（v4.9.1 P4.5 用户安全基础）
// 首次启动必看：彩票记录工具定位 / 不预测 / 不保证中奖 / 自主购彩

Page({
  data: {
    agreed: false,
  },

  onAgreeChange(e) {
    this.setData({ agreed: e.detail.value.length > 0 })
  },

  agreeAndContinue() {
    if (!this.data.agreed) {
      wx.showToast({ title: '请先阅读并同意协议', icon: 'none' })
      return
    }
    wx.setStorageSync('atlas_terms_agreed', true)
    wx.redirectTo({ url: '/pages/onboarding/index' })
  },
})
