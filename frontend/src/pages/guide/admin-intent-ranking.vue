<template>
	<view class="page">
		<view class="toolbar">
			<button class="ghost-btn" @click="goBack">返回上一页</button>
			<button class="solid-btn" @click="loadRecordList">刷新数据</button>
		</view>

		<view v-if="accessChecked" class="panel-card hero-card">
			<view class="card-head">
				<text class="card-title">意向记录总览</text>
				<text class="card-tip">
					进入页面时会在云端先聚合最新意向记录，再按双方互选与匹配总分生成排行榜，页面只接收聚合后的配对结果。
				</text>
			</view>

			<view class="stats-wrap">
				<view class="stat-card">
					<text class="stat-label">配对总数</text>
					<text class="stat-value">{{ summaryStats.totalPairs }}</text>
				</view>
				<view class="stat-card">
					<text class="stat-label">当前展示</text>
					<text class="stat-value">{{ summaryStats.filteredPairs }}</text>
				</view>
				<view class="stat-card">
					<text class="stat-label">匹配总分</text>
					<text class="stat-value">{{ formatScoreValue(summaryStats.totalMatchScore) }}</text>
				</view>
				<view class="stat-card">
					<text class="stat-label">{{ isWeightedPanel ? '最低总分' : '最高匹配分' }}</text>
					<text class="stat-value">{{ formatScoreValue(isWeightedPanel ? summaryStats.lowestMatchScore : summaryStats.topMatchScore) }}</text>
				</view>
			</view>
		</view>

		<view v-if="accessChecked" class="panel-card switch-card">
			<view class="switch-card-head">
				<view class="card-head">
					<text class="card-title">榜单切换</text>
					<text class="card-tip">切换不同计算方式的排行榜，筛选条件已经合并到榜单卡片内。</text>
				</view>
				<view class="panel-tabs">
					<view
						v-for="item in panelOptions"
						:key="item.value"
						class="panel-tab"
						:class="activePanel === item.value ? 'panel-tab is-active' : 'panel-tab'"
						@click="switchPanel(item.value)"
					>
						{{ item.label }}
					</view>
				</view>
			</view>
		</view>

		<view v-if="accessChecked" class="panel-card">
			<view class="card-head">
				<text class="card-title">{{ currentPanelMeta.title }}</text>
				<text class="card-tip">{{ currentPanelMeta.tip }}</text>
			</view>

			<view class="filter-box">
				<input
					v-model.trim="keyword"
					class="search-input filter-search-input"
					placeholder="搜索编号 / 姓名 / 昵称 / 用户ID / MBTI / 分数"
					confirm-type="search"
				/>
				<scroll-view class="status-scroll" scroll-x>
					<view class="status-row">
						<view
							v-for="item in statusOptions"
							:key="item.value"
							class="status-chip"
							:class="statusFilter === item.value ? 'status-chip active' : 'status-chip'"
							@click="changeStatus(item.value)"
						>
							{{ item.label }}
						</view>
					</view>
				</scroll-view>
			</view>

			<view class="table-shell">
				<scroll-view
					scroll-x
					scroll-y
					class="table-scroll"
					:scroll-top="tableScrollTop"
					:scroll-left="tableScrollLeft"
					@scroll="handleTableScroll"
				>
					<view class="table">
						<view class="table-row table-header">
							<text class="col col-rank">排行</text>
							<text class="col col-score">{{ isWeightedPanel ? '总分' : '匹配总分' }}</text>
							<text class="col col-pair">配对双方</text>
							<text class="col col-status">状态</text>
							<text class="col col-pair-rank">{{ isWeightedPanel ? '双方排名' : '双方志愿' }}</text>
							<text class="col col-expand">明细</text>
						</view>

						<view v-if="!loading && !recordList.length" class="empty-box">
							<text>当前没有可展示的互选配对</text>
						</view>
						<view v-else-if="!loading && !filteredRecordList.length" class="empty-box">
							<text>当前筛选条件下没有匹配结果</text>
						</view>

						<block v-for="item in pagedRecordList" :key="item.pair_key">
							<view
								class="table-row body-row is-expandable"
								:class="isPairExpanded(item.pair_key) ? 'is-expanded' : ''"
								@click="togglePairDetail(item.pair_key)"
							>
								<text class="col col-rank rank-text">#{{ item.pair_rank }}</text>
								<text class="col col-score score-strong">{{ formatScoreValue(item.match_score_total) }}</text>
								<view class="col col-pair pair-cell">
									<view class="pair-person pair-person-inline">
										<text class="primary-text">#{{ item.left_person.person_id || '-' }} · {{ item.left_person.name || '-' }}</text>
										<text class="secondary-text">{{ item.left_person.nickname || '未填写昵称' }} · {{ item.left_person.mbti || 'MBTI 未知' }}</text>
									</view>
									<text class="pair-divider">VS</text>
									<view class="pair-person pair-person-inline">
										<text class="primary-text">#{{ item.right_person.person_id || '-' }} · {{ item.right_person.name || '-' }}</text>
										<text class="secondary-text">{{ item.right_person.nickname || '未填写昵称' }} · {{ item.right_person.mbti || 'MBTI 未知' }}</text>
									</view>
								</view>
								<view class="col col-status">
									<text class="status-pill" :class="statusClass(item.pair_status)">
										{{ statusText(item.pair_status) }}
									</text>
								</view>
								<text class="col col-pair-rank">{{ formatRankValue(item.rank_left_to_right) }} / {{ formatRankValue(item.rank_right_to_left) }}</text>
								<view class="col col-expand expand-cell">
									<text class="expand-text">{{ isPairExpanded(item.pair_key) ? '收起 ▲' : '展开 ▼' }}</text>
								</view>
							</view>

							<view v-if="isPairExpanded(item.pair_key)" class="detail-panel">
								<view class="detail-head">
									<text class="detail-title">配对明细</text>
									<text class="detail-summary">
										总分 {{ formatScoreValue(item.match_score_total) }} 分 · 双方排名 {{ formatRankValue(item.rank_left_to_right) }} / {{ formatRankValue(item.rank_right_to_left) }}
									</text>
								</view>
								<view class="formula-card">
									<text class="formula-title">得分细节</text>
									<block v-if="isWeightedPanel">
										<text class="formula-text">
											{{ item.left_person.name || 'A' }} → {{ item.right_person.name || 'B' }}：{{ formatWeightedScoreText(item.rank_left_to_right, item.score_left_to_right) }}
										</text>
										<text class="formula-text">
											{{ item.right_person.name || 'B' }} → {{ item.left_person.name || 'A' }}：{{ formatWeightedScoreText(item.rank_right_to_left, item.score_right_to_left) }}
										</text>
										<text class="formula-result">
											总分 = {{ formatScoreValue(item.score_left_to_right) }} + {{ formatScoreValue(item.score_right_to_left) }} = {{ formatScoreValue(item.match_score_total) }}
										</text>
									</block>
									<block v-else>
										<text class="formula-text">
											{{ item.left_person.name || 'A' }} → {{ item.right_person.name || 'B' }}：{{ formatScoreValue(item.score_left_to_right) }} 分
										</text>
										<text class="formula-text">
											{{ item.right_person.name || 'B' }} → {{ item.left_person.name || 'A' }}：{{ formatScoreValue(item.score_right_to_left) }} 分
										</text>
										<text class="formula-text">
											互选加成：1.2 × min({{ formatScoreValue(item.score_left_to_right) }}, {{ formatScoreValue(item.score_right_to_left) }}) = {{ formatScoreValue(item.mutual_bonus_score) }}
										</text>
										<text class="formula-result">
											总分 = {{ formatScoreValue(item.score_left_to_right) }} + {{ formatScoreValue(item.score_right_to_left) }} + {{ formatScoreValue(item.mutual_bonus_score) }} = {{ formatScoreValue(item.match_score_total) }}
										</text>
									</block>
								</view>
								<view class="pick-list">
									<view class="pick-card">
										<view class="pick-top">
											<text class="pick-rank">{{ item.left_person.name || '-' }}</text>
											<text class="pick-nickname">{{ item.left_person.nickname || '未填写昵称' }}</text>
											<text class="pick-mbti">{{ item.left_person.mbti || 'MBTI 未知' }}</text>
											<text class="pick-state" :class="statusClass(item.left_status)">
												{{ statusText(item.left_status) }}
											</text>
										</view>
										<text class="pick-meta">编号 #{{ item.left_person.person_id || '-' }} · 选择对象 {{ item.right_person.name || '-' }}</text>
										<view class="pick-score-row">
											<text class="pick-score">志愿排名 {{ formatRankValue(item.rank_left_to_right) }}</text>
											<text class="pick-score">给分 {{ formatScoreValue(item.score_left_to_right) }}</text>
										</view>
										<text class="pick-meta">提交 {{ formatDate(item.left_submitted_at) }} · 更新 {{ formatDate(item.left_updated_at) }}</text>
									</view>
									<view class="pick-card">
										<view class="pick-top">
											<text class="pick-rank">{{ item.right_person.name || '-' }}</text>
											<text class="pick-nickname">{{ item.right_person.nickname || '未填写昵称' }}</text>
											<text class="pick-mbti">{{ item.right_person.mbti || 'MBTI 未知' }}</text>
											<text class="pick-state" :class="statusClass(item.right_status)">
												{{ statusText(item.right_status) }}
											</text>
										</view>
										<text class="pick-meta">编号 #{{ item.right_person.person_id || '-' }} · 选择对象 {{ item.left_person.name || '-' }}</text>
										<view class="pick-score-row">
											<text class="pick-score">志愿排名 {{ formatRankValue(item.rank_right_to_left) }}</text>
											<text class="pick-score">给分 {{ formatScoreValue(item.score_right_to_left) }}</text>
										</view>
										<text class="pick-meta">提交 {{ formatDate(item.right_submitted_at) }} · 更新 {{ formatDate(item.right_updated_at) }}</text>
									</view>
								</view>
							</view>
						</block>
					</view>
				</scroll-view>

				<view v-if="loading" class="table-loading-mask">
					<view class="table-loading-card">
						<text class="table-loading-text">正在加载{{ currentPanelMeta.title }}...</text>
					</view>
				</view>
			</view>

			<view v-if="totalCount > pagination.pageSize" class="table-pagination">
				<uni-pagination
					show-icon
					:current="pagination.page"
					:page-size="pagination.pageSize"
					:total="totalCount"
					@change="handlePageChange"
				/>
			</view>
		</view>
	</view>
</template>

<script>
const PERSONNEL_PROFILE_STORAGE_KEY = 'mbtiPersonnelProfile'
const STATUS_OPTIONS = [
	{ value: 'all', label: '全部状态' },
	{ value: 'draft', label: '草稿' },
	{ value: 'submitted', label: '已提交' },
	{ value: 'locked', label: '已锁定' }
]
const PANEL_OPTIONS = [
	{
		value: 'ranking',
		label: '配对排行榜',
		title: '配对排行榜',
		tip: '主表展示互选配对结果，按匹配总分从高到低排序。'
	},
	{
		value: 'weighted',
		label: '正序权重榜',
		title: '正序权重榜',
		tip: '双方进入前 10 名按名次正序计分，未进入前 10 名的一侧按 1000 权重计算，总分越低越靠前。'
	}
]
import { personnelUserService } from '@/api/modules/personnel-user'

let personnelUser = personnelUserService

function normalizeText(value) {
	return String(value || '').trim()
}

function normalizeKeyword(value) {
	return normalizeText(value).toLowerCase()
}

function normalizeUserId(value) {
	return normalizeText(value)
}

function normalizeMbti(value) {
	return normalizeText(value).toUpperCase()
}

function toNumber(value) {
	var num = Number(value)
	return Number.isFinite(num) ? num : 0
}

function normalizeRankSortValue(value) {
	var rank = toNumber(value)
	return rank > 0 ? rank : 999
}

function isDeletedRecord(value) {
	return (
		value === true ||
		value === 1 ||
		value === '1' ||
		String(value || '').toLowerCase() === 'true'
	)
}

function resolveTimeMs(value) {
	if (!value) {
		return 0
	}
	if (value instanceof Date) {
		return value.getTime()
	}
	if (typeof value === 'number') {
		return value > 1000000000000 ? value : value * 1000
	}
	if (typeof value === 'string') {
		var stringTime = Date.parse(value)
		return Number.isNaN(stringTime) ? 0 : stringTime
	}
	if (typeof value === 'object') {
		if (typeof value.getTime === 'function') {
			return value.getTime()
		}
		if (typeof value.toDate === 'function') {
			var converted = value.toDate()
			return converted instanceof Date ? converted.getTime() : 0
		}
		if (typeof value.$date === 'number') {
			return value.$date
		}
		if (typeof value.value === 'number') {
			return value.value
		}
		if (typeof value.timestamp === 'number') {
			return value.timestamp
		}
		if (typeof value.seconds === 'number') {
			return value.seconds * 1000
		}
	}
	return 0
}

function statusOrder(status) {
	if (status === 'locked') {
		return 3
	}
	if (status === 'submitted') {
		return 2
	}
	return 1
}

function roundScore(value) {
	return Math.round(toNumber(value))
}

function formatCompactChineseNumber(value) {
	var rounded = roundScore(value)
	var absValue = Math.abs(rounded)
	var unitList = [
		{ value: 1000000000000, label: '万亿' },
		{ value: 100000000, label: '亿' },
		{ value: 10000, label: '万' },
		{ value: 1000, label: '千' }
	]

	for (var i = 0; i < unitList.length; i += 1) {
		var currentUnit = unitList[i]
		if (absValue >= currentUnit.value) {
			var scaled = rounded / currentUnit.value
			var precision = absValue >= currentUnit.value * 100 ? 0 : 1
			return `${scaled.toFixed(precision).replace(/\.0$/, '')}${currentUnit.label}`
		}
	}

	return String(rounded)
}

export default {
	data() {
		return {
			currentUserRole: 0,
			accessChecked: false,
			activePanel: 'ranking',
			loading: false,
			keyword: '',
			keywordTimer: null,
			loadSequence: 0,
			statusFilter: 'all',
			expandedPairKey: '',
			tableScrollTop: 0,
			tableScrollLeft: 0,
			panelOptions: PANEL_OPTIONS,
			statusOptions: STATUS_OPTIONS,
			recordList: [],
			totalCount: 0,
			remoteStats: null,
			pagination: {
				page: 1,
				pageSize: 5
			}
		}
	},
	computed: {
		currentPanelMeta() {
			var currentPanel = this.panelOptions.find(
				function (item) {
					return item.value === this.activePanel
				}.bind(this)
			)
			return currentPanel || PANEL_OPTIONS[0]
		},
		isWeightedPanel() {
			return this.activePanel === 'weighted'
		},
		filteredRecordList() {
			return this.recordList
		},
		pagedRecordList() {
			return this.recordList
		},
		summaryStats() {
			if (this.remoteStats) {
				return {
					totalPairs: toNumber(this.remoteStats.totalPairs),
					filteredPairs: toNumber(this.remoteStats.filteredPairs),
					totalMatchScore: toNumber(this.remoteStats.totalMatchScore),
					topMatchScore: toNumber(this.remoteStats.topMatchScore),
					lowestMatchScore: toNumber(this.remoteStats.lowestMatchScore)
				}
			}
			return {
				totalPairs: this.totalCount,
				filteredPairs: this.recordList.length,
				totalMatchScore: 0,
				topMatchScore: 0,
				lowestMatchScore: 0
			}
		}
	},
	watch: {
		activePanel() {
			this.resetListPosition(true)
			this.loadRecordList()
		},
		keyword() {
			this.resetListPosition(true)
			this.scheduleKeywordReload()
		},
		statusFilter() {
			this.resetListPosition(true)
			this.loadRecordList()
		}
	},
	onUnload() {
		if (this.keywordTimer) {
			clearTimeout(this.keywordTimer)
			this.keywordTimer = null
		}
	},
	onLoad() {
		this.currentUserRole = this.getCurrentUserRole()
		if (!this.ensurePageAccess()) {
			return
		}
		this.accessChecked = true
		this.loadRecordList()
	},
	methods: {
		getCurrentUserRole() {
			try {
				var profile = uni.getStorageSync(PERSONNEL_PROFILE_STORAGE_KEY)
				return Number(profile && profile.user_role) || 0
			} catch (error) {
				console.error('getCurrentUserRole failed', error)
				return 0
			}
		},
		ensurePageAccess() {
			if (Number(this.currentUserRole) >= 1) {
				return true
			}
			uni.showModal({
				title: '权限不足',
				content: '当前账号暂无查看意向记录页面的权限。',
				showCancel: false,
				success: () => {
					this.goBack()
				}
			})
			return false
		},
		goBack() {
			var pageStack = getCurrentPages()
			if (pageStack.length > 1) {
				uni.navigateBack({ delta: 1 })
				return
			}
			uni.reLaunch({ url: '/pkg/guide/hub' })
		},
		switchPanel(value) {
			this.activePanel = value === 'weighted' ? 'weighted' : 'ranking'
		},
		resetListPosition(resetPage) {
			if (resetPage) {
				this.pagination.page = 1
			}
			this.expandedPairKey = ''
			this.tableScrollTop = 0
			this.tableScrollLeft = 0
		},
		scheduleKeywordReload() {
			if (this.keywordTimer) {
				clearTimeout(this.keywordTimer)
			}
			this.keywordTimer = setTimeout(
				function () {
					this.keywordTimer = null
					this.loadRecordList()
				}.bind(this),
				260
			)
		},
		changeStatus(value) {
			this.statusFilter = value
		},
		handlePageChange(event) {
			var current = Number(event && event.current)
			this.pagination.page = current > 0 ? current : 1
			this.resetListPosition(false)
			this.loadRecordList()
		},
		handleTableScroll(event) {
			var detail = (event && event.detail) || {}
			this.tableScrollTop = toNumber(detail.scrollTop)
			this.tableScrollLeft = toNumber(detail.scrollLeft)
		},
		isPairExpanded(pairKey) {
			return normalizeText(pairKey) && this.expandedPairKey === normalizeText(pairKey)
		},
		togglePairDetail(pairKey) {
			var normalizedPairKey = normalizeText(pairKey)
			this.expandedPairKey = this.expandedPairKey === normalizedPairKey ? '' : normalizedPairKey
		},
		buildIdentityKey(recordId, userId, personId) {
			var normalizedRecordId = normalizeText(recordId)
			if (normalizedRecordId) {
				return `record:${normalizedRecordId}`
			}
			var normalizedOpenid = normalizeUserId(userId)
			if (normalizedOpenid) {
				return `userId:${normalizedOpenid}`
			}
			var normalizedPersonId = toNumber(personId)
			return normalizedPersonId ? `person:${normalizedPersonId}` : ''
		},
		buildPairKey(activityId, creatorKey, targetKey) {
			return [normalizeText(activityId), normalizeText(creatorKey), normalizeText(targetKey)].join('::')
		},
		buildCanonicalPairKey(activityId, leftKey, rightKey) {
			var keyList = [normalizeText(leftKey), normalizeText(rightKey)].sort()
			return [normalizeText(activityId), keyList[0], keyList[1]].join('::')
		},
		mergePersonProfile(profileMap, personKey, payload) {
			var normalizedPersonKey = normalizeText(personKey)
			if (!normalizedPersonKey) {
				return
			}
			if (!profileMap[normalizedPersonKey]) {
				profileMap[normalizedPersonKey] = {
					person_key: normalizedPersonKey,
					record_id: '',
					person_id: 0,
					user_id: '',
					wx_userId: '',
					name: '',
					nickname: '',
					mbti: ''
				}
			}

			var profile = profileMap[normalizedPersonKey]
			var recordId = normalizeText(payload && payload.record_id)
			var personId = toNumber(payload && payload.person_id)
			var userId = normalizeText(payload && payload.user_id)
			var wxOpenid = normalizeUserId(payload && payload.wx_userId)
			var name = normalizeText(payload && payload.name)
			var nickname = normalizeText(payload && payload.nickname)
			var mbti = normalizeMbti(payload && payload.mbti)

			if (!profile.record_id && recordId) {
				profile.record_id = recordId
			}
			if (!profile.person_id && personId) {
				profile.person_id = personId
			}
			if (!profile.user_id && userId) {
				profile.user_id = userId
			}
			if (!profile.wx_userId && wxOpenid) {
				profile.wx_userId = wxOpenid
			}
			if (!profile.name && name) {
				profile.name = name
			}
			if (!profile.nickname && nickname) {
				profile.nickname = nickname
			}
			if (!profile.mbti && mbti) {
				profile.mbti = mbti
			}
		},
		buildPersonView(profileMap, personKey) {
			var normalizedPersonKey = normalizeText(personKey)
			var profile = profileMap[normalizedPersonKey] || {}
			return {
				person_key: normalizedPersonKey,
				record_id: normalizeText(profile.record_id),
				person_id: toNumber(profile.person_id),
				user_id: normalizeText(profile.user_id),
				wx_userId: normalizeUserId(profile.wx_userId),
				name: normalizeText(profile.name),
				nickname: normalizeText(profile.nickname),
				mbti: normalizeMbti(profile.mbti)
			}
		},
		comparePersonView(leftPerson, rightPerson) {
			var leftPersonId = toNumber(leftPerson && leftPerson.person_id)
			var rightPersonId = toNumber(rightPerson && rightPerson.person_id)
			if (leftPersonId && rightPersonId && leftPersonId !== rightPersonId) {
				return leftPersonId - rightPersonId
			}
			var leftName = normalizeText(leftPerson && leftPerson.name)
			var rightName = normalizeText(rightPerson && rightPerson.name)
			if (leftName !== rightName) {
				return leftName.localeCompare(rightName)
			}
			return normalizeText(leftPerson && leftPerson.person_key).localeCompare(
				normalizeText(rightPerson && rightPerson.person_key)
			)
		},
		resolvePairStatus(leftStatus, rightStatus) {
			var normalizedLeftStatus = normalizeText(leftStatus) || 'draft'
			var normalizedRightStatus = normalizeText(rightStatus) || 'draft'
			return statusOrder(normalizedLeftStatus) <= statusOrder(normalizedRightStatus)
				? normalizedLeftStatus
				: normalizedRightStatus
		},
		normalizeRow(item) {
			var creatorKey = this.buildIdentityKey(
				item && item.creator_record_id,
				item && item.creator_wx_userId,
				item && item.creator_person_id
			)
			var targetKey = this.buildIdentityKey(
				item && item.target_record_id,
				item && item.target_wx_userId,
				item && item.target_person_id
			)
			return {
				_id: normalizeText(item && item._id),
				activity_id: normalizeText(item && item.activity_id),
				creator_record_id: normalizeText(item && item.creator_record_id),
				creator_person_id: toNumber(item && item.creator_person_id),
				creator_user_id: normalizeText(item && item.creator_user_id),
				creator_wx_userId: normalizeUserId(item && item.creator_wx_userId),
				creator_name: normalizeText(item && item.creator_name),
				creator_nickname: normalizeText(item && item.creator_nickname),
				target_record_id: normalizeText(item && item.target_record_id),
				target_person_id: toNumber(item && item.target_person_id),
				target_user_id: normalizeText(item && item.target_user_id),
				target_wx_userId: normalizeUserId(item && item.target_wx_userId),
				target_name: normalizeText(item && item.target_name),
				target_nickname: normalizeText(item && item.target_nickname),
				target_mbti: normalizeMbti(item && item.target_mbti),
				rank: toNumber(item && item.rank),
				score: toNumber(item && item.score),
				submit_status: normalizeText(item && item.submit_status) || 'draft',
				submitted_at: (item && item.submitted_at) || '',
				deadline_at: (item && item.deadline_at) || '',
				created_at: (item && item.created_at) || '',
				updated_at: (item && item.updated_at) || '',
				remark: normalizeText(item && item.remark),
				creator_key: creatorKey,
				target_key: targetKey
			}
		},
		buildRecordViewList(rawList) {
			var rowList = (Array.isArray(rawList) ? rawList : [])
				.filter(function (item) {
					return !isDeletedRecord(item && item.is_deleted)
				})
				.map(
					function (item) {
						return this.normalizeRow(item)
					}.bind(this)
				)
				.filter(function (item) {
					return !!(item.activity_id && item.creator_key && item.target_key)
				})

			var directionMap = {}
			var personProfileMap = {}

			rowList.forEach(
				function (item) {
					var directionKey = this.buildPairKey(item.activity_id, item.creator_key, item.target_key)
					var currentDirectionRecord = directionMap[directionKey]
					if (
						!currentDirectionRecord ||
						resolveTimeMs(item.updated_at) > resolveTimeMs(currentDirectionRecord.updated_at)
					) {
						directionMap[directionKey] = item
					}

					this.mergePersonProfile(personProfileMap, item.creator_key, {
						record_id: item.creator_record_id,
						person_id: item.creator_person_id,
						user_id: item.creator_user_id,
						wx_userId: item.creator_wx_userId,
						name: item.creator_name,
						nickname: item.creator_nickname
					})
					this.mergePersonProfile(personProfileMap, item.target_key, {
						record_id: item.target_record_id,
						person_id: item.target_person_id,
						user_id: item.target_user_id,
						wx_userId: item.target_wx_userId,
						name: item.target_name,
						nickname: item.target_nickname,
						mbti: item.target_mbti
					})
				}.bind(this)
			)

			var pairVisitedMap = {}

			return Object.keys(directionMap)
				.map(
					function (directionKey) {
						var row = directionMap[directionKey]
						if (!row || row.creator_key === row.target_key) {
							return null
						}

						var reciprocalKey = this.buildPairKey(row.activity_id, row.target_key, row.creator_key)
						var reciprocalRow = directionMap[reciprocalKey] || null
						if (!reciprocalRow) {
							return null
						}

						var canonicalPairKey = this.buildCanonicalPairKey(
							row.activity_id,
							row.creator_key,
							row.target_key
						)
						if (pairVisitedMap[canonicalPairKey]) {
							return null
						}
						pairVisitedMap[canonicalPairKey] = true

						var leftRow = row
						var rightRow = reciprocalRow
						var leftPerson = this.buildPersonView(personProfileMap, leftRow.creator_key)
						var rightPerson = this.buildPersonView(personProfileMap, leftRow.target_key)

						if (this.comparePersonView(leftPerson, rightPerson) > 0) {
							leftRow = reciprocalRow
							rightRow = row
							leftPerson = this.buildPersonView(personProfileMap, leftRow.creator_key)
							rightPerson = this.buildPersonView(personProfileMap, leftRow.target_key)
						}

						var scoreLeftToRight = toNumber(leftRow.score)
						var scoreRightToLeft = toNumber(rightRow.score)
						var mutualBonus = Math.min(scoreLeftToRight, scoreRightToLeft) * 1.2

						return {
							pair_key: canonicalPairKey,
							activity_id: leftRow.activity_id,
							left_person: leftPerson,
							right_person: rightPerson,
							pair_status: this.resolvePairStatus(leftRow.submit_status, rightRow.submit_status),
							left_status: leftRow.submit_status,
							right_status: rightRow.submit_status,
							score_left_to_right: scoreLeftToRight,
							score_right_to_left: scoreRightToLeft,
							mutual_bonus_score: Number.isInteger(mutualBonus) ? mutualBonus : Number(mutualBonus.toFixed(1)),
							match_score_total: scoreLeftToRight + scoreRightToLeft + mutualBonus,
							best_single_score: Math.max(scoreLeftToRight, scoreRightToLeft),
							rank_left_to_right: toNumber(leftRow.rank),
							rank_right_to_left: toNumber(rightRow.rank),
							left_submitted_at: leftRow.submitted_at,
							right_submitted_at: rightRow.submitted_at,
							left_updated_at: leftRow.updated_at,
							right_updated_at: rightRow.updated_at,
							submitted_at:
								resolveTimeMs(leftRow.submitted_at) > resolveTimeMs(rightRow.submitted_at)
									? leftRow.submitted_at
									: rightRow.submitted_at,
							deadline_at:
								resolveTimeMs(leftRow.deadline_at) > resolveTimeMs(rightRow.deadline_at)
									? leftRow.deadline_at
									: rightRow.deadline_at,
							updated_at:
								resolveTimeMs(leftRow.updated_at) > resolveTimeMs(rightRow.updated_at)
									? leftRow.updated_at
									: rightRow.updated_at
						}
					}.bind(this)
				)
				.filter(function (item) {
					return !!item
				})
				.sort(function (a, b) {
					var scoreDiff = toNumber(b.match_score_total) - toNumber(a.match_score_total)
					if (scoreDiff !== 0) {
						return scoreDiff
					}
					var bestSingleScoreDiff = toNumber(b.best_single_score) - toNumber(a.best_single_score)
					if (bestSingleScoreDiff !== 0) {
						return bestSingleScoreDiff
					}
					var rankDiff =
						normalizeRankSortValue(a.rank_left_to_right) +
						normalizeRankSortValue(a.rank_right_to_left) -
						normalizeRankSortValue(b.rank_left_to_right) -
						normalizeRankSortValue(b.rank_right_to_left)
					if (rankDiff !== 0) {
						return rankDiff
					}
					var timeDiff = resolveTimeMs(b.updated_at) - resolveTimeMs(a.updated_at)
					if (timeDiff !== 0) {
						return timeDiff
					}
					return a.pair_key.localeCompare(b.pair_key)
				})
				.map(function (item, index) {
					item.pair_rank = index + 1
					return item
				})
		},
		async loadRecordList() {
			if (!this.accessChecked) {
				return
			}
			if (!personnelUser) {
				uni.showModal({
					content: '当前环境不支持云对象调用。',
					showCancel: false
				})
				return
			}
			this.loading = true
			var currentLoadSequence = this.loadSequence + 1
			this.loadSequence = currentLoadSequence
			try {
				var result =
					this.activePanel === 'weighted'
						? await personnelUser.listIntentWeightedPairRankings({
								keyword: this.keyword,
								status: this.statusFilter,
								page: this.pagination.page,
								pageSize: this.pagination.pageSize
							})
						: await personnelUser.listIntentPairRankings({
								keyword: this.keyword,
								status: this.statusFilter,
								page: this.pagination.page,
								pageSize: this.pagination.pageSize
							})
				if (currentLoadSequence !== this.loadSequence) {
					return
				}
				this.recordList = (result && result.list) || []
				this.totalCount = toNumber(result && result.total)
				this.remoteStats = (result && result.stats) || null
				this.pagination.page = toNumber(result && result.page) || this.pagination.page
				this.pagination.pageSize = toNumber(result && result.pageSize) || this.pagination.pageSize
			} catch (error) {
				if (currentLoadSequence !== this.loadSequence) {
					return
				}
				console.error('loadRecordList failed', error)
				uni.showToast({
					title: error.message || '记录加载失败',
					icon: 'none'
				})
			} finally {
				this.loading = false
			}
		},
		statusText(status) {
			if (status === 'submitted') {
				return '已提交'
			}
			if (status === 'locked') {
				return '已锁定'
			}
			return '草稿'
		},
		statusClass(status) {
			if (status === 'submitted') {
				return 'status-submitted'
			}
			if (status === 'locked') {
				return 'status-locked'
			}
			return 'status-draft'
		},
		formatRankValue(value) {
			var rank = toNumber(value)
			return rank > 0 ? `#${rank}` : '前十外'
		},
		formatScoreValue(value) {
			return formatCompactChineseNumber(value)
		},
		formatWeightedScoreText(rank, score) {
			var normalizedRank = toNumber(rank)
			var normalizedScore = this.formatScoreValue(score)
			if (normalizedRank > 0) {
				return `排名 ${normalizedRank}，计 ${normalizedScore} 分`
			}
			return `未进入前 10，按 ${normalizedScore || '1000'} 权重计算`
		},
		formatDate(value) {
			if (!value) {
				return '-'
			}
			var time = resolveTimeMs(value)
			if (!time) {
				var text = normalizeText(value)
				return text ? text.replace('T', ' ').slice(0, 19) : '-'
			}
			var date = new Date(time)
			var year = date.getFullYear()
			var month = `${date.getMonth() + 1}`.padStart(2, '0')
			var day = `${date.getDate()}`.padStart(2, '0')
			var hours = `${date.getHours()}`.padStart(2, '0')
			var minutes = `${date.getMinutes()}`.padStart(2, '0')
			return `${year}-${month}-${day} ${hours}:${minutes}`
		}
	}
}
</script>

<style scoped lang="less">
.page {
	min-height: 100vh;
	padding: 24rpx;
	background: #f5efe5;
	box-sizing: border-box;
}

.toolbar {
	display: flex;
	flex-wrap: wrap;
	margin-bottom: 20rpx;
}

.panel-card,
.stat-card {
	background: #fffcf7;
	border: 1rpx solid #eadfce;
	border-radius: 28rpx;
	box-shadow: 0 18rpx 40rpx rgba(91, 70, 40, 0.08);
}

.panel-card {
	padding: 32rpx 28rpx;
	margin-bottom: 24rpx;
}

.card-head {
	display: flex;
	flex-direction: column;
}

.switch-card-head {
	display: flex;
	flex-direction: column;
}

.card-title {
	font-size: 32rpx;
	font-weight: 700;
	color: #2d241c;
}

.card-tip,
.secondary-text,
.pick-meta,
.detail-summary {
	margin-top: 16rpx;
	font-size: 24rpx;
	line-height: 1.7;
	color: #716250;
}

.panel-tabs {
	display: flex;
	flex-wrap: wrap;
	align-self: flex-start;
	margin-top: 24rpx;
	padding: 8rpx;
	border-radius: 999rpx;
	background: #f4ecde;
}

.panel-tab {
	padding: 16rpx 28rpx;
	border-radius: 999rpx;
	font-size: 24rpx;
	line-height: 1;
	color: #6d4e2c;
	white-space: nowrap;
	transition: all 0.2s ease;
}

.panel-tab.is-active {
	background: #1f6b52;
	color: #ffffff;
	box-shadow: 0 10rpx 24rpx rgba(31, 107, 82, 0.16);
}

.filter-box {
	margin-top: 24rpx;
	padding: 24rpx;
	border-radius: 24rpx;
	background: #fbf8f2;
	border: 1rpx solid #eadfce;
}

.stats-wrap,
.status-row,
.pick-top,
.pick-score-row {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
}

.stats-wrap {
	justify-content: space-between;
	flex-wrap: nowrap;
	margin-top: 24rpx;
}

.stat-card {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: flex-start;
	width: 23.5%;
	margin-bottom: 0;
	padding: 24rpx 16rpx;
	min-height: 148rpx;
	box-sizing: border-box;
}

.stat-label {
	display: block;
	font-size: 24rpx;
	line-height: 1.4;
	color: #7c6b57;
}

.stat-value {
	display: block;
	margin-top: 12rpx;
	font-size: 40rpx;
	line-height: 1.1;
	font-weight: 700;
	color: #2e241b;
}

.search-input {
	width: 100%;
	height: 84rpx;
	padding: 0 24rpx;
	line-height: 84rpx;
	margin-top: 24rpx;
	background: #fbf8f2;
	border: 1rpx solid #dfd3c1;
	border-radius: 20rpx;
	box-sizing: border-box;
	color: #342b22;
	font-size: 26rpx;
}

.filter-search-input {
	margin-top: 0;
}

.status-scroll {
	width: 100%;
	margin-top: 20rpx;
}

.status-row {
	padding-bottom: 8rpx;
}

.status-chip {
	padding: 14rpx 24rpx;
	margin-right: 16rpx;
	border-radius: 999rpx;
	background: #efe5d3;
	color: #6d4e2c;
	font-size: 24rpx;
	white-space: nowrap;
}

.status-chip.active {
	background: #1f6b52;
	color: #ffffff;
}

.table-scroll {
	width: 100%;
	margin-top: 24rpx;
	height: 68vh;
	max-height: 1280rpx;
	min-height: 720rpx;
	border: 1rpx solid #eadfce;
	border-radius: 24rpx;
	background: #fffaf3;
	box-sizing: border-box;
}

.table-shell {
	position: relative;
}

.table {
	width: 1320rpx;
	min-width: 1320rpx;
}

.table-row {
	display: flex;
	flex-wrap: nowrap;
	align-items: stretch;
	border-bottom: 1rpx solid #eadfce;
}

.table-header {
	background: #f4ecde;
	border-radius: 20rpx 20rpx 0 0;
}

.body-row {
	background: rgba(255, 255, 255, 0.72);
}

.col {
	padding: 22rpx 16rpx;
	font-size: 24rpx;
	color: #46382b;
	box-sizing: border-box;
	white-space: nowrap;
}

.col-rank { width: 120rpx; }
.col-pair {
	width: 580rpx;
	white-space: normal;
}
.col-status { width: 160rpx; }
.col-score { width: 160rpx; }
.col-pair-rank { width: 180rpx; }
.col-expand { width: 140rpx; }

.is-expandable {
	transition: background-color 0.2s ease;
}

.is-expandable.is-expanded {
	background: rgba(245, 236, 222, 0.9);
}

.pair-cell,
.pair-person {
	display: flex;
	flex-direction: column;
}

.pair-cell {
	flex-direction: row;
	align-items: stretch;
	gap: 16rpx;
}

.pair-person {
	flex: 1;
	min-width: 0;
	padding: 18rpx 16rpx;
	border-radius: 18rpx;
	background: rgba(244, 236, 222, 0.58);
}

.pair-person-inline {
	justify-content: center;
}

.pair-divider {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	align-self: center;
	flex: 0 0 56rpx;
	height: 56rpx;
	border-radius: 999rpx;
	background: #efe5d3;
	color: #6d4e2c;
	font-size: 22rpx;
	font-weight: 700;
}

.primary-text {
	font-size: 28rpx;
	font-weight: 700;
	color: #2d241c;
	white-space: normal;
	word-break: break-word;
}

.pair-cell .secondary-text {
	margin-top: 10rpx;
	white-space: normal;
	word-break: break-word;
}

.rank-text {
	font-weight: 700;
	color: #1f6b52;
}

.expand-cell {
	display: flex;
	align-items: center;
	justify-content: center;
}

.expand-text {
	font-size: 24rpx;
	font-weight: 700;
	color: #6d4e2c;
}

.status-pill,
.pick-state,
.pick-mbti {
	display: inline-flex;
	align-items: center;
	padding: 10rpx 18rpx;
	border-radius: 999rpx;
	font-size: 22rpx;
	white-space: nowrap;
}

.status-draft {
	background: #efe5d3;
	color: #6d4e2c;
}

.status-submitted {
	background: #dff4e8;
	color: #1e6b45;
}

.status-locked {
	background: #fce3ad;
	color: #7a4a12;
}

.score-strong {
	font-weight: 700;
	color: #1f6b52;
}

.detail-panel {
	padding: 24rpx;
	border-bottom: 1rpx solid #eadfce;
	background: #fffaf3;
}

.detail-head {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	justify-content: space-between;
}

.detail-title {
	font-size: 28rpx;
	font-weight: 700;
	color: #2d241c;
}

.detail-summary {
	margin-top: 0;
}

.formula-card {
	margin-top: 20rpx;
	padding: 20rpx 24rpx;
	border-radius: 20rpx;
	background: #fff3dc;
	border: 1rpx solid #efd6a8;
}

.formula-title {
	font-size: 26rpx;
	font-weight: 700;
	color: #7a4a12;
}

.formula-text,
.formula-result {
	display: block;
	margin-top: 12rpx;
	font-size: 24rpx;
	line-height: 1.7;
	color: #5b4630;
	word-break: break-word;
}

.formula-result {
	font-weight: 700;
	color: #1f6b52;
}

.pick-list {
	display: flex;
	flex-wrap: wrap;
	justify-content: space-between;
	margin-top: 20rpx;
}

.pick-card {
	width: 49%;
	margin-bottom: 18rpx;
	padding: 20rpx;
	border-radius: 24rpx;
	background: #ffffff;
	border: 1rpx solid #eadfce;
	box-sizing: border-box;
}

.pick-rank {
	font-size: 24rpx;
	font-weight: 700;
	color: #1f6b52;
}

.pick-name {
	margin-left: 14rpx;
	font-size: 28rpx;
	font-weight: 700;
	color: #2d241c;
}

.pick-nickname {
	margin-left: 12rpx;
	font-size: 24rpx;
	color: #716250;
}

.pick-mbti {
	margin-left: 12rpx;
	background: #f3eadb;
	color: #5e472e;
}

.pick-state {
	margin-left: auto;
}

.pick-meta {
	display: block;
	word-break: break-all;
}

.pick-score-row {
	margin-top: 14rpx;
}

.pick-score {
	margin-right: 18rpx;
	font-size: 24rpx;
	color: #46382b;
}

.empty-box {
	padding: 44rpx 24rpx;
	font-size: 26rpx;
	color: #857362;
	text-align: center;
}

.table-loading-mask {
	position: absolute;
	top: 24rpx;
	right: 0;
	bottom: 0;
	left: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 24rpx;
	background: rgba(255, 250, 243, 0.72);
	backdrop-filter: blur(4px);
	z-index: 5;
}

.table-loading-card {
	padding: 22rpx 30rpx;
	border-radius: 999rpx;
	background: rgba(255, 255, 255, 0.96);
	border: 1rpx solid rgba(234, 223, 206, 0.9);
	box-shadow: 0 16rpx 32rpx rgba(109, 78, 44, 0.08);
}

.table-loading-text {
	font-size: 26rpx;
	font-weight: 700;
	color: #6d4e2c;
}

.table-pagination {
	padding-top: 24rpx;
	display: flex;
	justify-content: flex-end;
}

.solid-btn,
.ghost-btn {
	height: 76rpx;
	line-height: 76rpx;
	padding: 0 28rpx;
	border-radius: 999rpx;
	font-size: 26rpx;
	margin: 0 20rpx 0 0;
}

.solid-btn {
	background: #1f6b52;
	color: #ffffff;
}

.ghost-btn {
	background: #efe5d3;
	color: #6d4e2c;
}

@media screen and (max-width: 768px) {
	.panel-tabs {
		width: 100%;
		border-radius: 24rpx;
	}

	.panel-tab {
		flex: 1;
		text-align: center;
	}

	.table-scroll {
		height: 60vh;
		min-height: 880rpx;
	}

	.pair-cell {
		gap: 12rpx;
	}

	.pair-divider {
		flex-basis: 48rpx;
		width: 48rpx;
		height: 48rpx;
		font-size: 20rpx;
	}

	.pick-card {
		width: 100%;
	}
}
</style>
