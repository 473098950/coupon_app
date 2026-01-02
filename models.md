User（微信用户 / 管理员）
  ├─ roles = ['consumer', 'merchant', 'admin']
  ├─ merchant（OneToOne，可空）
  ├─ wallet

Merchant（商家主体）
  ├─ user（OneToOne，可空）
  ├─ 抽成比例
  ├─ 资质 / 图片 / 经营数据

MembershipCard（会员卡）
  ├─ user
  ├─ source_merchant（扫码来源）

CouponRule（优惠规则）
  ├─ merchant

Redemption（核销）
  ├─ merchant
  ├─ user
  ├─ membership_card

Referral（推荐奖励）