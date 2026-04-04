-- 心动消息明细表
-- 业务来源：user-message-center.vue / admin-heart-message-management.vue
-- 设计原则：通过 sender_record_id / receiver_record_id 逻辑关联 personnel_user._id，不创建物理外键

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

USE `in_grace`;

CREATE TABLE IF NOT EXISTS `personnel_heart_message` (
  `_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '消息ID，如 heart-20260404-001',
  `conversation_key` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '会话键，双方 personnel_user._id 按字典序拼接',
  `sender_record_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '发送方 personnel_user._id',
  `receiver_record_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '接收方 personnel_user._id',
  `content` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '消息内容',
  `status` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft' COMMENT '状态:draft/queued/delivered/revoked',
  `is_anonymous` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否匿名发送',
  `quota_cost` smallint UNSIGNED NOT NULL DEFAULT 1 COMMENT '消耗心动值',
  `message_scene` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'chat' COMMENT '消息场景:chat/inbox/manual',
  `user_remark` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '用户备注/后台备注',
  `created_at` datetime(3) NOT NULL COMMENT '创建时间',
  `updated_at` datetime(3) NOT NULL COMMENT '更新时间',
  `delivered_at` datetime(3) DEFAULT NULL COMMENT '投递时间',
  `revoked_at` datetime(3) DEFAULT NULL COMMENT '撤销时间',
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '软删除',
  PRIMARY KEY (`_id`),
  KEY `idx_personnel_heart_message_conversation_created` (`conversation_key`, `created_at`),
  KEY `idx_personnel_heart_message_sender_created` (`sender_record_id`, `created_at`),
  KEY `idx_personnel_heart_message_receiver_created` (`receiver_record_id`, `created_at`),
  KEY `idx_personnel_heart_message_status` (`status`),
  KEY `idx_personnel_heart_message_scene` (`message_scene`),
  KEY `idx_personnel_heart_message_deleted` (`is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='心动消息明细表';

ALTER TABLE `personnel_heart_message`
  CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO `personnel_heart_message` (
  `_id`,
  `conversation_key`,
  `sender_record_id`,
  `receiver_record_id`,
  `content`,
  `status`,
  `is_anonymous`,
  `quota_cost`,
  `message_scene`,
  `user_remark`,
  `created_at`,
  `updated_at`,
  `delivered_at`,
  `revoked_at`,
  `is_deleted`
)
VALUES
  (
    'heart-20260404-001',
    'personnel-204::personnel-205',
    'personnel-204',
    'personnel-205',
    '第一次看到你的介绍，感觉你很真诚，想先悄悄和你打个招呼。',
    'delivered',
    1,
    1,
    'inbox',
    '匿名来信',
    '2026-04-03 20:30:00.000',
    '2026-04-03 20:30:00.000',
    '2026-04-03 20:30:00.000',
    NULL,
    0
  ),
  (
    'heart-20260404-002',
    'personnel-204::personnel-205',
    'personnel-205',
    'personnel-204', 
    '谢谢你的来信，我也愿意慢慢认识你。',
    'delivered',
    0,
    1,
    'chat',
    '',
    '2026-04-03 21:00:00.000',
    '2026-04-03 21:00:00.000',
    '2026-04-03 21:00:00.000',
    NULL,
    0
  ),
  (
    'heart-20260404-003',
    'personnel-205::personnel-207',
    'personnel-207',
    'personnel-205',
    '你的节奏感让我很安心，如果你愿意，我想继续了解你。',
    'delivered',
    1,
    1,
    'inbox',
    '匿名来信',
    '2026-04-04 09:20:00.000',
    '2026-04-04 09:20:00.000',
    '2026-04-04 09:20:00.000',
    NULL,
    0
  ),
  (
    'heart-20260404-004',
    'personnel-205::personnel-208',
    'personnel-208',
    'personnel-205',
    '想约你在主日后一起喝杯咖啡，可以吗？',
    'queued',
    1,
    1,
    'inbox',
    '待投递匿名来信',
    '2026-04-04 11:10:00.000',
    '2026-04-04 11:10:00.000',
    NULL,
    NULL,
    0
  ),
  (
    'heart-20260404-005',
    'personnel-205::personnel-209',
    'personnel-205',
    'personnel-209',
    '看见你也喜欢稳定而真诚的关系，想认真认识一下你。',
    'delivered',
    0,
    1,
    'chat',
    '',
    '2026-04-04 12:00:00.000',
    '2026-04-04 12:00:00.000',
    '2026-04-04 12:00:00.000',
    NULL,
    0
  ),
  (
    'heart-20260404-006',
    'personnel-210::personnel-212',
    'personnel-210',
    'personnel-212',
    '这是一条管理员预置草稿，用于测试后台编辑态。',
    'draft',
    1,
    1,
    'manual',
    '后台草稿',
    '2026-04-04 12:30:00.000',
    '2026-04-04 12:30:00.000',
    NULL,
    NULL,
    0
  ),
  (
    'heart-20260404-007',
    'personnel-204::personnel-211',
    'personnel-211',
    'personnel-204',
    '这是一条已撤销消息，用于测试后台状态筛选。',
    'revoked',
    1,
    1,
    'manual',
    '管理员撤销',
    '2026-04-04 08:00:00.000',
    '2026-04-04 08:10:00.000',
    NULL,
    '2026-04-04 08:10:00.000',
    0
  ),
  (
    'heart-20260404-008',
    'personnel-207::personnel-210',
    'personnel-210',
    'personnel-207',
    '很高兴在活动里认识你，期待下次再聊。',
    'delivered',
    0,
    1,
    'chat',
    '活动后跟进',
    '2026-04-04 13:00:00.000',
    '2026-04-04 13:00:00.000',
    '2026-04-04 13:00:00.000',
    NULL,
    0
  )
ON DUPLICATE KEY UPDATE
  `conversation_key` = VALUES(`conversation_key`),
  `sender_record_id` = VALUES(`sender_record_id`),
  `receiver_record_id` = VALUES(`receiver_record_id`),
  `content` = VALUES(`content`),
  `status` = VALUES(`status`),
  `is_anonymous` = VALUES(`is_anonymous`),
  `quota_cost` = VALUES(`quota_cost`),
  `message_scene` = VALUES(`message_scene`),
  `user_remark` = VALUES(`user_remark`),
  `created_at` = VALUES(`created_at`),
  `updated_at` = VALUES(`updated_at`),
  `delivered_at` = VALUES(`delivered_at`),
  `revoked_at` = VALUES(`revoked_at`),
  `is_deleted` = VALUES(`is_deleted`);

SET FOREIGN_KEY_CHECKS = 1;
