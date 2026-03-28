<template>
	<view class="page">
		<view class="toolbar">
			<button class="ghost-btn" @click="goBack">返回上一页</button>
			<button class="solid-btn" @click="loadPairGroups">刷新查询</button>
		</view>

		<view class="summary-card">
			<text class="summary-title">MBTI 组合配对查询</text>
			<view class="summary-stats">
				<view class="stat-item">
					<text class="stat-label">总人数</text>
					<text class="stat-value">{{ displayTotalMembers }}</text>
				</view>
				<view class="stat-item">
					<text class="stat-label">可配对人数</text>
					<text class="stat-value">{{ displayValidMembers }}</text>
				</view>
				<view class="stat-item">
					<text class="stat-label">配对数量</text>
					<text class="stat-value">{{ displayTotalPairs }}</text>
				</view>
				<view class="stat-item">
					<text class="stat-label">分组数</text>
					<text class="stat-value">{{ displayGroupCount }}</text>
				</view>
			</view>
		</view>

		<view class="filter-card">
			<input
				v-model.trim="filterKeyword"
				class="search-input"
				placeholder="筛选组合 / 别名 / 成员姓名 / MBTI"
				confirm-type="search"
			/>
			<text class="filter-tip">支持按组合、别名、成员姓名或 MBTI 或 姓名x姓名 关键词筛选</text>
		</view>

		<view v-if="loading" class="state-box state-panel">
			<text>正在计算组合，请稍候...</text>
		</view>
		<view v-else-if="!groupList.length" class="state-box state-panel">
			<text>暂无可配对数据，请先补充人员 MBTI。</text>
		</view>
		<view v-else-if="!displayGroupList.length" class="state-box state-panel">
			<text>当前筛选条件下暂无匹配组合。</text>
		</view>

		<view v-else class="result-panel" @click="closeMemberDetail">
			<scroll-view class="group-list-scroll" scroll-y>
				<view class="group-list">
					<view v-for="group in pagedGroupList" :key="group.key" class="group-card">
						<view class="group-head">
							<text class="group-name"
								>{{ group.name
								}}<text v-if="group.subname" class="group-subname"
									>（{{ group.subname }}）</text
								></text
							>
							<text class="group-meta">{{ group.pairs.length }} 对</text>
						</view>
						<view class="pair-rating-row group-rating-row">
							<text
								class="pair-rating-badge"
								:class="'pair-rating-' + getScoreAssessment(group.compatibilityScore).key"
								@click.stop="showMatchReason(group)"
							>
								{{ getScoreAssessment(group.compatibilityScore).label }} ·
								{{ group.compatibilityScore }}分
							</text>
						</view>
						<text class="group-combos"
							>组合：{{ group.comboSummary }}｜成员池：{{ group.memberSummary }}</text
						>

						<scroll-view class="table-scroll" scroll-x @click.stop>
							<view class="table">
								<view class="table-row table-header">
									<text class="col col-member">{{ group.leftMbti }} 成员</text>
									<text class="col col-member">{{ group.rightMbti }} 成员</text>
								</view>
								<block v-for="pair in group.pairs" :key="pair.key">
									<view class="table-row">
										<view
											class="col col-member member-cell"
											:class="
												selectedDetailTarget &&
												selectedDetailTarget.pairKey === pair.key &&
												selectedDetailTarget.side === 'left'
													? 'member-cell active'
													: ''
											"
											@click.stop="toggleMemberDetail(pair, 'left')"
										>
											<text
												class="member-link"
												:class="getMemberGenderClass(pair.leftMember)"
											>
												{{ pair.leftName }}（{{ pair.leftMbti }}） {{ getMemberGenderSymbol(pair.leftMember) }}
											</text>
										</view>
										<view
											class="col col-member member-cell"
											:class="
												selectedDetailTarget &&
												selectedDetailTarget.pairKey === pair.key &&
												selectedDetailTarget.side === 'right'
													? 'member-cell active'
													: ''
											"
											@click.stop="toggleMemberDetail(pair, 'right')"
										>
											<text
												class="member-link"
												:class="getMemberGenderClass(pair.rightMember)"
											>
												{{ pair.rightName }}（{{ pair.rightMbti }}{{ getMemberGenderSymbol(pair.rightMember) }}）
											</text>
										</view>
									</view>
									<view v-if="isPairMemberSelected(pair)" class="detail-row" @click.stop>
										<view class="member-detail-card">
											<view class="member-detail-head">
												<view>
													<text class="member-detail-title">{{
														selectedMemberDetail.displayName || '-'
													}}</text>
													<text class="member-detail-subtitle"
														>编号：{{ selectedMemberDetail.person_id || '-' }} · MBTI：{{
															selectedMemberDetail.mbti || '-'
														}}</text
													>
												</view>
												<text class="member-detail-close" @click.stop="closeMemberDetail"
													>收起</text
												>
											</view>
											<!-- <text class="member-detail-tip">点击其他空白区域也可收起</text> -->
											<image
												v-if="selectedMemberDetail.personal_photo"
												class="member-detail-photo"
												:src="selectedMemberDetail.personal_photo"
												mode="aspectFill"
											></image>
											<view class="member-detail-grid">
												<text class="member-detail-item"
													>姓名：{{ selectedMemberDetail.name || '-' }}</text
												>
												<text class="member-detail-item"
													>昵称：{{ selectedMemberDetail.nickname || '-' }}</text
												>
												<text class="member-detail-item"
													>性别：{{ selectedMemberDetail.gender || '-' }}</text
												>
												<text class="member-detail-item"
													>年龄：{{ selectedMemberDetail.age || '-' }}</text
												>
												<text class="member-detail-item"
													>手机：{{ selectedMemberDetail.mobile || '-' }}</text
												>
												<text class="member-detail-item"
													>籍贯：{{ selectedMemberDetail.native_place || '-' }}</text
												>
												<text class="member-detail-item"
													>职业：{{ selectedMemberDetail.profession || '-' }}</text
												>
												<text class="member-detail-item"
													>教会：{{ selectedMemberDetail.church || '-' }}</text
												>
												<text class="member-detail-item"
													>推荐人：{{ selectedMemberDetail.referrer || '-' }}</text
												>
												<text class="member-detail-item"
													>感情状态：{{ selectedMemberDetail.relationship_status || '-' }}</text
												>
												<text class="member-detail-item"
													>出行方式：{{ selectedMemberDetail.travel_mode || '-' }}</text
												>
											</view>
											<view v-if="selectedMemberDetail.address" class="member-detail-block">
												<text class="member-detail-block-title">地址</text>
												<text class="member-detail-block-text">{{
													selectedMemberDetail.address
												}}</text>
											</view>
											<view v-if="selectedMemberDetail.family_overview" class="member-detail-block">
												<text class="member-detail-block-title">家庭概况</text>
												<text class="member-detail-block-text">{{
													selectedMemberDetail.family_overview
												}}</text>
											</view>
											<view
												v-if="selectedMemberDetail.self_introduction"
												class="member-detail-block"
											>
												<text class="member-detail-block-title">自我介绍</text>
												<text class="member-detail-block-text">{{
													selectedMemberDetail.self_introduction
												}}</text>
											</view>
										</view>
									</view>
								</block>
							</view>
						</scroll-view>
					</view>
				</view>
			</scroll-view>
			<view v-if="paginationTotal > pagination.pageSize" class="pagination-wrap">
				<view
					class="pager-btn"
					:class="isFirstPage ? 'pager-btn is-disabled' : ''"
					@click="goPrevPage"
					>上一页</view
				>
				<text class="pager-text">第 {{ pagination.page }} / {{ totalPages }} 页</text>
				<view
					class="pager-btn"
					:class="isLastPage ? 'pager-btn is-disabled' : ''"
					@click="goNextPage"
					>下一页</view
				>
			</view>
		</view>
	</view>
</template>

<script>
	import relationshipSource from '@/data/mbti_16x16_relationships_full.json'

var db = null
if (typeof uniCloud !== 'undefined' && uniCloud.database) {
	db = uniCloud.database()
}
var PAIR_GROUP_CACHE_KEY = 'MBTI_PAIR_GROUP_CACHE_V1'
var PAIR_GROUP_CACHE_VERSION = 1

	var RELATIONSHIP_LIST = (relationshipSource && relationshipSource.mbti_relationships_full) || []

	function normalizeMbtiValue(value) {
		return String(value || '')
			.trim()
			.toUpperCase()
	}

	function buildComboKey(typeA, typeB) {
		var comboTypes = [normalizeMbtiValue(typeA), normalizeMbtiValue(typeB)]
			.filter(function (item) {
				return !!item
			})
			.sort()

		return comboTypes.join('+')
	}

	function buildRelationshipConfigs(list) {
		var configList = []
		var configMap = {}

		for (var i = 0; i < list.length; i++) {
			var item = list[i] || {}
			var comboKey = buildComboKey(item.type_a, item.type_b)
			if (!comboKey || configMap[comboKey]) {
				continue
			}

			var comboTypes = comboKey.split('+')
			var config = {
				key: comboKey,
				comboKey: comboKey,
				leftMbti: comboTypes[0] || '',
				rightMbti: comboTypes[1] || comboTypes[0] || '',
				subname: String(item.cp_name || '').trim(),
				matchReason: String(item.match_reason || '').trim(),
				riskPoints: Array.isArray(item.risk_points) ? item.risk_points : [],
				relationshipLevel: String(item.relationship_level || '').trim(),
				compatibilityScore: Number(item.compatibility_score) || 0
			}

			configList.push(config)
			configMap[comboKey] = config
		}

		return {
			list: configList,
			map: configMap
		}
	}

	var RELATIONSHIP_CONFIGS = buildRelationshipConfigs(RELATIONSHIP_LIST)
	var RELATIONSHIP_CONFIG_LIST = RELATIONSHIP_CONFIGS.list
	var RELATIONSHIP_CONFIG_MAP = RELATIONSHIP_CONFIGS.map
	var SUPPORTED_MBTI_MAP = {}

	for (
		var relationshipIndex = 0;
		relationshipIndex < RELATIONSHIP_CONFIG_LIST.length;
		relationshipIndex++
	) {
		var relationshipConfig = RELATIONSHIP_CONFIG_LIST[relationshipIndex]
		SUPPORTED_MBTI_MAP[relationshipConfig.leftMbti] = true
		SUPPORTED_MBTI_MAP[relationshipConfig.rightMbti] = true
	}

	export default {
		data() {
			return {
				loading: false,
				totalMembers: 0,
				validMembers: 0,
				totalPairs: 0,
				groupList: [],
				selectedMemberDetail: null,
				selectedDetailTarget: null,
				filterKeyword: '',
				pagination: {
					page: 1,
					pageSize: 5
				}
			}
		},
		computed: {
			displayGroupList() {
				// 当前页面的搜索是在前端本地完成：
				// 先拿到全部人员并生成配对结果，再根据关键词过滤和调整展示顺序。
				var keyword = this.normalizeKeyword(this.filterKeyword)
				if (!keyword) {
					return this.groupList
				}

				return this.groupList
					.map(
						function (group) {
							var matchedPairs = group.pairs.filter(
								function (pair) {
									return this.matchesGroupKeyword(group, pair, keyword)
								}.bind(this)
							)

							if (!matchedPairs.length) {
								return null
							}

							return this.reorderGroupForKeyword(
								Object.assign({}, group, {
									pairs: matchedPairs
								}),
								keyword
							)
						}.bind(this)
					)
					.filter(function (group) {
						return !!group
					})
			},
			paginationTotal() {
				return this.displayGroupList.length
			},
			displaySummary() {
				var keyword = this.normalizeKeyword(this.filterKeyword)
				if (!keyword) {
					return {
						totalMembers: this.totalMembers,
						validMembers: this.validMembers,
						totalPairs: this.totalPairs,
						groupCount: this.groupList.length
					}
				}

				var memberMap = {}
				var matchedMemberCount = 0
				var totalPairs = 0

				for (var i = 0; i < this.displayGroupList.length; i++) {
					var group = this.displayGroupList[i]
					totalPairs += group.pairs.length
					for (var j = 0; j < group.pairs.length; j++) {
						var pair = group.pairs[j]
						var leftId = pair.leftMember && pair.leftMember._id
						var rightId = pair.rightMember && pair.rightMember._id

						if (leftId && !memberMap[leftId]) {
							memberMap[leftId] = true
							matchedMemberCount += 1
						}

						if (rightId && !memberMap[rightId]) {
							memberMap[rightId] = true
							matchedMemberCount += 1
						}
					}
				}

				return {
					totalMembers: matchedMemberCount,
					validMembers: matchedMemberCount,
					totalPairs: totalPairs,
					groupCount: this.displayGroupList.length
				}
			},
			displayTotalMembers() {
				return this.displaySummary.totalMembers
			},
			displayValidMembers() {
				return this.displaySummary.validMembers
			},
			displayTotalPairs() {
				return this.displaySummary.totalPairs
			},
			displayGroupCount() {
				return this.displaySummary.groupCount
			},
			totalPages() {
				return Math.max(1, Math.ceil(this.paginationTotal / Number(this.pagination.pageSize || 5)))
			},
			isFirstPage() {
				return Number(this.pagination.page || 1) <= 1
			},
			isLastPage() {
				return Number(this.pagination.page || 1) >= this.totalPages
			},
			pagedGroupList() {
				// 这里的分页只是前端展示分页，不是云端按 5 条查询。
				var pageSize = Number(this.pagination.pageSize || 5)
				var total = this.displayGroupList.length
				var maxPage = Math.max(1, Math.ceil(total / pageSize))
				var currentPage = Number(this.pagination.page || 1)
				if (currentPage < 1) {
					currentPage = 1
				}
				if (currentPage > maxPage) {
					currentPage = maxPage
				}
				var start = (currentPage - 1) * pageSize
				return this.displayGroupList.slice(start, start + pageSize)
			}
		},
		watch: {
			filterKeyword() {
				this.resetPagination()
			},
			groupList() {
				this.resetPagination()
			},
			displayGroupList(list) {
				this.syncPagination(list.length)
			}
		},
		onLoad() {
			this.restorePairGroupsFromCache()
		},
		methods: {
			restorePairGroupsFromCache() {
				try {
					var cachedPayload = uni.getStorageSync(PAIR_GROUP_CACHE_KEY)
					if (
						!cachedPayload ||
						typeof cachedPayload !== 'object' ||
						Number(cachedPayload.version || 0) !== PAIR_GROUP_CACHE_VERSION
					) {
						return
					}
					this.applyPairGroupsResult(cachedPayload)
				} catch (error) {
					console.error('restorePairGroupsFromCache failed', error)
				}
			},
			applyPairGroupsResult(payload) {
				var safePayload = payload || {}
				this.selectedMemberDetail = null
				this.selectedDetailTarget = null
				this.totalMembers = Number(safePayload.totalMembers || 0)
				this.validMembers = Number(safePayload.validMembers || 0)
				this.totalPairs = Number(safePayload.totalPairs || 0)
				this.groupList = Array.isArray(safePayload.groupList) ? safePayload.groupList : []
				this.syncPagination(this.groupList.length)
			},
			savePairGroupsToCache(payload) {
				try {
					uni.setStorageSync(PAIR_GROUP_CACHE_KEY, {
						version: PAIR_GROUP_CACHE_VERSION,
						updatedAt: Date.now(),
						totalMembers: Number(payload.totalMembers || 0),
						validMembers: Number(payload.validMembers || 0),
						totalPairs: Number(payload.totalPairs || 0),
						groupList: Array.isArray(payload.groupList) ? payload.groupList : []
					})
				} catch (error) {
					console.error('savePairGroupsToCache failed', error)
				}
			},
			goBack() {
				var pageStack = getCurrentPages()
				if (pageStack.length > 1) {
					uni.navigateBack({ delta: 1 })
					return
				}
				uni.reLaunch({
					url: '/pkg/guide/hub'
				})
			},
			normalizeMbti(value) {
				return normalizeMbtiValue(value)
			},
			normalizeKeyword(value) {
				return String(value || '')
					.trim()
					.toUpperCase()
			},
			getDisplayName(item) {
				return item.name || item.nickname || '#' + (item.person_id || '')
			},
			parsePairKeyword(keyword) {
				var rawKeyword = String(keyword || '').trim()
				if (!rawKeyword) {
					return null
				}

				var parts = rawKeyword
					.split(/[xX×]/)
					.map(
						function (item) {
							return this.normalizeKeyword(item)
						}.bind(this)
					)
					.filter(function (item) {
						return !!item
					})

				if (parts.length !== 2) {
					return null
				}

				return {
					leftKeyword: parts[0],
					rightKeyword: parts[1]
				}
			},
			formatMemberSummary(leftMbti, leftCount, rightMbti, rightCount) {
				if (leftMbti === rightMbti) {
					return leftMbti + '：' + leftCount + ' 人'
				}
				return leftMbti + '：' + leftCount + ' 人 / ' + rightMbti + '：' + rightCount + ' 人'
			},
			getScoreAssessment(score) {
				var value = Number(score) || 0
				if (value >= 90) {
					return { key: 's', label: '顶配组合' }
				}
				if (value >= 82) {
					return { key: 'a', label: '高匹配' }
				}
				if (value >= 72) {
					return { key: 'b', label: '值得尝试' }
				}
				if (value >= 60) {
					return { key: 'c', label: '需要磨合' }
				}
				return { key: 'd', label: '挑战较高' }
			},
			showMatchReason(group) {
				if (!group) {
					return
				}
				var contentList = []
				if (group.matchReason) {
					contentList.push('匹配原因：' + group.matchReason)
				}
				if (group.riskPoints && group.riskPoints.length) {
					contentList.push(
						'风险点：\n' +
							group.riskPoints
								.map(function (item, index) {
									return index + 1 + '. ' + item
								})
								.join('\n')
					)
				}
				uni.showModal({
					title: group.name || '匹配原因',
					content: contentList.join('\n\n') || '当前暂无匹配原因说明',
					showCancel: false,
					confirmText: '我知道了'
				})
			},
			formatGroupName(leftMbti, rightMbti) {
				var left = this.normalizeMbti(leftMbti)
				var right = this.normalizeMbti(rightMbti)
				if (!left && !right) {
					return ''
				}
				if (!right || left === right) {
					return left + ' 组'
				}
				return left + ' + ' + right + ' 组'
			},
			swapPairDisplay(pair) {
				return Object.assign({}, pair, {
					leftName: pair.rightName,
					leftMbti: pair.rightMbti,
					leftMember: pair.rightMember,
					rightName: pair.leftName,
					rightMbti: pair.leftMbti,
					rightMember: pair.leftMember
				})
			},
			pairMatchesKeywordSide(pair, keyword, side) {
				if (!pair || !keyword) {
					return false
				}
				var name = side === 'right' ? pair.rightName : pair.leftName
				var mbti = side === 'right' ? pair.rightMbti : pair.leftMbti
				var haystack = [name, mbti].join('|').toUpperCase()
				return haystack.indexOf(keyword) !== -1
			},
			pairMatchesCombinedKeyword(pair, keyword) {
				var pairKeyword = this.parsePairKeyword(keyword)
				if (!pairKeyword || !pair) {
					return false
				}

				var leftMatchesLeft = this.pairMatchesKeywordSide(pair, pairKeyword.leftKeyword, 'left')
				var leftMatchesRight = this.pairMatchesKeywordSide(pair, pairKeyword.leftKeyword, 'right')
				var rightMatchesLeft = this.pairMatchesKeywordSide(pair, pairKeyword.rightKeyword, 'left')
				var rightMatchesRight = this.pairMatchesKeywordSide(pair, pairKeyword.rightKeyword, 'right')

				return (leftMatchesLeft && rightMatchesRight) || (leftMatchesRight && rightMatchesLeft)
			},
			resolvePreferredLeftMbti(group, keyword) {
				var pairKeyword = this.parsePairKeyword(keyword)
				if (pairKeyword) {
					for (var pairIndex = 0; pairIndex < group.pairs.length; pairIndex++) {
						var keywordPair = group.pairs[pairIndex]
						if (this.pairMatchesKeywordSide(keywordPair, pairKeyword.leftKeyword, 'left')) {
							return keywordPair.leftMbti
						}
						if (this.pairMatchesKeywordSide(keywordPair, pairKeyword.leftKeyword, 'right')) {
							return keywordPair.rightMbti
						}
					}
				}

				var normalizedKeyword = this.normalizeMbti(keyword)
				if (normalizedKeyword && this.isSupportedMbti(normalizedKeyword)) {
					return normalizedKeyword
				}

				for (var i = 0; i < group.pairs.length; i++) {
					var pair = group.pairs[i]
					if (this.pairMatchesKeywordSide(pair, keyword, 'left')) {
						return pair.leftMbti
					}
					if (this.pairMatchesKeywordSide(pair, keyword, 'right')) {
						return pair.rightMbti
					}
				}

				return ''
			},
			reorderPairForKeyword(pair, keyword, preferredLeftMbti) {
				if (!pair) {
					return pair
				}

				if (
					preferredLeftMbti &&
					pair.rightMbti === preferredLeftMbti &&
					pair.leftMbti !== preferredLeftMbti
				) {
					return this.swapPairDisplay(pair)
				}

				if (
					!preferredLeftMbti &&
					this.pairMatchesKeywordSide(pair, keyword, 'right') &&
					!this.pairMatchesKeywordSide(pair, keyword, 'left')
				) {
					return this.swapPairDisplay(pair)
				}

				return pair
			},
			reorderGroupForKeyword(group, keyword) {
				if (!group || !keyword) {
					return group
				}

				var preferredLeftMbti = this.resolvePreferredLeftMbti(group, keyword)
				if (!preferredLeftMbti) {
					return group
				}

				var displayPairs = group.pairs.map(
					function (pair) {
						return this.reorderPairForKeyword(pair, keyword, preferredLeftMbti)
					}.bind(this)
				)

				var shouldKeepOriginalLeft = group.leftMbti === preferredLeftMbti
				var shouldSwap =
					group.rightMbti === preferredLeftMbti && group.leftMbti !== preferredLeftMbti

				if (!shouldKeepOriginalLeft && !shouldSwap) {
					return Object.assign({}, group, {
						pairs: displayPairs,
						name: this.formatGroupName(group.leftMbti, group.rightMbti)
					})
				}

				if (!shouldSwap) {
					return Object.assign({}, group, {
						name: this.formatGroupName(group.leftMbti, group.rightMbti),
						pairs: displayPairs,
						memberSummary: this.formatMemberSummary(
							group.leftMbti,
							group.leftCount,
							group.rightMbti,
							group.rightCount
						)
					})
				}

				return Object.assign({}, group, {
					name: this.formatGroupName(group.rightMbti, group.leftMbti),
					leftMbti: group.rightMbti,
					rightMbti: group.leftMbti,
					leftCount: group.rightCount,
					rightCount: group.leftCount,
					memberSummary: this.formatMemberSummary(
						group.rightMbti,
						group.rightCount,
						group.leftMbti,
						group.leftCount
					),
					pairs: displayPairs
				})
			},
			toggleMemberDetail(pair, side) {
				var member = side === 'right' ? pair && pair.rightMember : pair && pair.leftMember
				if (!pair || !member || !member._id) {
					return
				}
				if (
					this.selectedDetailTarget &&
					this.selectedDetailTarget.pairKey === pair.key &&
					this.selectedDetailTarget.side === side &&
					this.selectedDetailTarget.memberId === member._id
				) {
					this.selectedMemberDetail = null
					this.selectedDetailTarget = null
					return
				}
				this.selectedMemberDetail = member
				this.selectedDetailTarget = {
					pairKey: pair.key,
					side: side,
					memberId: member._id
				}
			},
			closeMemberDetail() {
				this.selectedMemberDetail = null
				this.selectedDetailTarget = null
			},
			isPairMemberSelected(pair) {
				if (!this.selectedMemberDetail || !this.selectedDetailTarget || !pair) {
					return false
				}
				return this.selectedDetailTarget.pairKey === pair.key
			},
			isSupportedMbti(value) {
				return !!SUPPORTED_MBTI_MAP[this.normalizeMbti(value)]
			},
			getGroupConfig(comboKey) {
				return RELATIONSHIP_CONFIG_MAP[comboKey] || null
			},
			resetPagination() {
				this.pagination.page = 1
			},
			syncPagination(total) {
				var pageSize = Number(this.pagination.pageSize || 5)
				var maxPage = Math.max(1, Math.ceil(Number(total || 0) / pageSize))
				if (this.pagination.page > maxPage) {
					this.pagination.page = maxPage
				}
				if (this.pagination.page < 1) {
					this.pagination.page = 1
				}
			},
			goPrevPage() {
				if (this.isFirstPage) {
					return
				}
				this.pagination.page = Number(this.pagination.page || 1) - 1
			},
			goNextPage() {
				if (this.isLastPage) {
					return
				}
				this.pagination.page = Number(this.pagination.page || 1) + 1
			},
			resolveGroupName(comboKey) {
				return comboKey + '组'
			},
			matchesGroupKeyword(group, pair, keyword) {
				if (this.pairMatchesCombinedKeyword(pair, keyword)) {
					return true
				}

				var haystack = [
					group.name,
					group.subname,
					group.comboSummary,
					group.memberSummary,
					group.leftMbti,
					group.rightMbti,
					pair.comboKey,
					pair.leftName,
					pair.leftMbti,
					pair.rightName,
					pair.rightMbti
				]
					.join('|')
					.toUpperCase()

				return haystack.indexOf(keyword) !== -1
			},
			buildMemberBucketMap(members) {
				var bucketMap = {}

				for (var i = 0; i < members.length; i++) {
					var member = members[i]
					if (!bucketMap[member.mbti]) {
						bucketMap[member.mbti] = []
					}
					bucketMap[member.mbti].push(member)
				}

				return bucketMap
			},
			normalizeGender(value) {
				var gender = String(value || '')
					.trim()
					.toLowerCase()

				if (!gender) {
					return ''
				}

				if (
					gender === '\u7537' ||
					gender === 'm' ||
					gender === 'male' ||
					gender === 'man' ||
					gender.indexOf('\u7537') !== -1
				) {
					return 'male'
				}

				if (
					gender === '\u5973' ||
					gender === 'f' ||
					gender === 'female' ||
					gender === 'woman' ||
					gender.indexOf('\u5973') !== -1
				) {
					return 'female'
				}

				return ''
			},
			isOppositeGenderPair(leftMember, rightMember) {
				var leftGender = this.normalizeGender(leftMember && leftMember.gender)
				var rightGender = this.normalizeGender(rightMember && rightMember.gender)
				if (!leftGender || !rightGender) {
					return false
				}
				return leftGender !== rightGender
			},
			getMemberGenderSymbol(member) {
				var gender = this.normalizeGender(member && member.gender)
				if (gender === 'male') {
					return '♂'
				}
				if (gender === 'female') {
					return '♀'
				}
				return ''
			},
			getMemberGenderClass(member) {
				var gender = this.normalizeGender(member && member.gender)
				if (gender === 'male') {
					return 'member-link-male'
				}
				if (gender === 'female') {
					return 'member-link-female'
				}
				return ''
			},
			createPairRecord(comboKey, left, right, compatibilityScore) {
				return {
					key: comboKey + '__' + left._id + '_' + right._id,
					comboKey: comboKey,
					compatibilityScore: Number(compatibilityScore) || 0,
					leftName: left.displayName,
					leftMbti: left.mbti,
					leftMember: left,
					rightName: right.displayName,
					rightMbti: right.mbti,
					rightMember: right
				}
			},
			buildGroupPairs(config, bucketMap) {
				var leftMembers = bucketMap[config.leftMbti] || []
				var rightMembers = bucketMap[config.rightMbti] || []
				var pairs = []

				if (config.leftMbti === config.rightMbti) {
					for (var i = 0; i < leftMembers.length; i++) {
						for (var j = i + 1; j < leftMembers.length; j++) {
							if (!this.isOppositeGenderPair(leftMembers[i], leftMembers[j])) {
								continue
							}
							pairs.push(
								this.createPairRecord(
									config.comboKey,
									leftMembers[i],
									leftMembers[j],
									config.compatibilityScore
								)
							)
						}
					}
				} else {
					for (var leftIndex = 0; leftIndex < leftMembers.length; leftIndex++) {
						for (var rightIndex = 0; rightIndex < rightMembers.length; rightIndex++) {
							if (
								!this.isOppositeGenderPair(
									leftMembers[leftIndex],
									rightMembers[rightIndex]
								)
							) {
								continue
							}
							pairs.push(
								this.createPairRecord(
									config.comboKey,
									leftMembers[leftIndex],
									rightMembers[rightIndex],
									config.compatibilityScore
								)
							)
						}
					}
				}

				return {
					pairs: pairs,
					leftCount: leftMembers.length,
					rightCount: rightMembers.length
				}
			},
			buildPairGroups(members) {
				var bucketMap = this.buildMemberBucketMap(members)
				var groupList = []
				var total = 0

				for (var i = 0; i < RELATIONSHIP_CONFIG_LIST.length; i++) {
					var config = RELATIONSHIP_CONFIG_LIST[i]
					var pairData = this.buildGroupPairs(config, bucketMap)
					if (!pairData.pairs.length) {
						continue
					}

					total += pairData.pairs.length
					groupList.push({
						key: config.key,
						name: this.resolveGroupName(config.comboKey),
						subname: config.subname,
						matchReason: config.matchReason,
						riskPoints: config.riskPoints,
						comboKey: config.comboKey,
						comboSummary: config.comboKey,
						leftMbti: config.leftMbti,
						rightMbti: config.rightMbti,
						leftCount: pairData.leftCount,
						rightCount: pairData.rightCount,
						memberSummary:
							config.leftMbti === config.rightMbti
								? config.leftMbti + '：' + pairData.leftCount + ' 人'
								: config.leftMbti +
									'：' +
									pairData.leftCount +
									' 人 / ' +
									config.rightMbti +
									'：' +
									pairData.rightCount +
									' 人',
						compatibilityScore: config.compatibilityScore,
						pairs: pairData.pairs
					})
				}

				groupList.sort(function (a, b) {
					if (b.compatibilityScore !== a.compatibilityScore) {
						return b.compatibilityScore - a.compatibilityScore
					}
					if (b.pairs.length !== a.pairs.length) {
						return b.pairs.length - a.pairs.length
					}
					return a.comboKey.localeCompare(b.comboKey)
				})

				return {
					totalPairs: total,
					groupList: groupList
				}
			},
			async fetchAllPersonnel() {
				// 这里会分批把人员数据从云端全部取回。
				// 单次最多取 500 条，循环直到取完为止。
				// 之后的搜索、配对、排序都在前端本地进行。
				var pageSize = 500
				var page = 0
				var allList = []

				while (true) {
					var res = await db
						.collection('mbti-personnel')
						.field(
							'_id,person_id,nickname,name,gender,age,personal_photo,mobile,mbti,native_place,profession,address,family_overview,church,referrer,self_introduction,relationship_status,travel_mode,is_deleted'
						)
						.orderBy('person_id', 'asc')
						.skip(page * pageSize)
						.limit(pageSize)
						.get()
					var currentList = (res.result && res.result.data) || res.data || []

					if (!currentList.length) {
						break
					}

					allList = allList.concat(currentList)
					if (currentList.length < pageSize) {
						break
					}

					page += 1
				}

				return allList
			},
			async loadPairGroups() {
				if (!db) {
					uni.showModal({
						content: '当前环境不支持云数据库查询',
						showCancel: false
					})
					return
				}
				this.loading = true
				try {
					var list = await this.fetchAllPersonnel()
					var activeList = list.filter(function (item) {
						var deletedValue = item && item.is_deleted
						return !(
							deletedValue === true ||
							deletedValue === 1 ||
							deletedValue === '1' ||
							String(deletedValue || '').toLowerCase() === 'true'
						)
					})
					var members = activeList
						.map(
							function (item) {
								var mbti = this.normalizeMbti(item.mbti)
								if (!mbti || !this.isSupportedMbti(mbti)) {
									return null
								}
								return {
									_id: item._id,
									person_id: item.person_id,
									nickname: item.nickname || '',
									name: item.name || '',
									gender: item.gender || '',
									age: item.age,
									personal_photo: item.personal_photo || '',
									mobile: item.mobile || '',
									mbti: mbti,
									native_place: item.native_place || '',
									profession: item.profession || '',
									address: item.address || '',
									family_overview: item.family_overview || '',
									church: item.church || '',
									referrer: item.referrer || '',
									self_introduction: item.self_introduction || '',
									relationship_status: item.relationship_status || '',
									travel_mode: item.travel_mode || '',
									displayName: this.getDisplayName(item)
								}
							}.bind(this)
						)
						.filter(function (item) {
							return !!item
						})

					var result = this.buildPairGroups(members)
					var resultPayload = {
						totalMembers: activeList.length,
						validMembers: members.length,
						totalPairs: result.totalPairs,
						groupList: result.groupList
					}
					this.applyPairGroupsResult(resultPayload)
					this.savePairGroupsToCache(resultPayload)
				} catch (error) {
					uni.showModal({
						content: error.message || '查询失败，请稍后重试',
						showCancel: false
					})
				} finally {
					this.loading = false
				}
			}
		}
	}
</script>

<style scoped lang="less">
	.page {
		height: 100vh;
		display: flex;
		flex-direction: column;
		padding: 24rpx;
		background: #f5efe5;
		box-sizing: border-box;
		overflow: hidden;
	}

	.toolbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 20rpx;
	}

	.solid-btn,
	.ghost-btn {
		height: 68rpx;
		line-height: 68rpx;
		padding: 0 28rpx;
		border-radius: 999rpx;
		font-size: 24rpx;
		margin: 0;
	}

	.solid-btn {
		background: #1f6b52;
		color: #ffffff;
	}

	.ghost-btn {
		background: #efe5d3;
		color: #6d4e2c;
	}

	.summary-card,
	.filter-card,
	.group-card,
	.state-box {
		background: #fffcf7;
		border: 1rpx solid #eadfce;
		border-radius: 24rpx;
		box-shadow: 0 14rpx 32rpx rgba(91, 70, 40, 0.08);
	}

	.summary-card {
		padding: 28rpx 24rpx;
	}

	.filter-card {
		margin-top: 20rpx;
		padding: 24rpx;
	}

	.search-input {
		height: 76rpx;
		padding: 0 24rpx;
		border-radius: 18rpx;
		background: #f6efe3;
		font-size: 24rpx;
		color: #2f261e;
		box-sizing: border-box;
	}

	.filter-tip {
		display: block;
		margin-top: 12rpx;
		font-size: 22rpx;
		color: #8a7560;
	}

	.summary-title {
		display: block;
		font-size: 34rpx;
		font-weight: 700;
		color: #2d241c;
	}

	.summary-desc {
		display: block;
		margin-top: 10rpx;
		font-size: 24rpx;
		color: #716250;
	}

	.summary-stats {
		display: flex;
		flex-wrap: nowrap;
		justify-content: space-between;
		gap: 12rpx;
		margin-top: 20rpx;
	}

	.stat-item {
		flex: 1;
		min-width: 0;
		margin-bottom: 0;
	}

	.stat-label {
		display: block;
		font-size: 22rpx;
		color: #8a7560;
		white-space: nowrap;
	}

	.stat-value {
		display: block;
		margin-top: 6rpx;
		font-size: 32rpx;
		font-weight: 700;
		color: #2e241b;
	}

	.state-box {
		margin-top: 20rpx;
		padding: 40rpx 24rpx;
		font-size: 26rpx;
		text-align: center;
		color: #6d5a47;
	}

	.state-panel {
		flex: 1;
		min-height: 0;
	}

	.result-panel {
		display: flex;
		flex: 1;
		flex-direction: column;
		min-height: 0;
		margin-top: 20rpx;
	}

	.group-list-scroll {
		flex: 1;
		min-height: 0;
	}

	.group-list {
		padding-bottom: 8rpx;
	}

	.pagination-wrap {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 20rpx;
		padding: 12rpx 0 4rpx;
	}

	.pager-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		min-width: 160rpx;
		height: 64rpx;
		line-height: 64rpx;
		padding: 0 24rpx;
		border-radius: 999rpx;
		font-size: 24rpx;
		color: #6d4e2c;
		background: #efe5d3;
		margin: 0;
	}

	.pager-btn.is-disabled {
		opacity: 0.45;
	}

	.pager-text {
		font-size: 24rpx;
		color: #7a6652;
	}

	.group-card {
		padding: 24rpx;
		margin-bottom: 20rpx;
	}

	.group-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.group-name {
		font-size: 30rpx;
		font-weight: 700;
		color: #2d241c;
	}

	.group-meta {
		font-size: 22rpx;
		color: #8e7962;
	}

	.group-subname {
		display: inline;
		font-size: 25rpx;
		color: #8f6840;
	}

	.group-score {
		display: inline;
		font-size: 24rpx;
		font-weight: 600;
		color: #8f6840;
	}

	.group-combos {
		display: block;
		margin-top: 10rpx;
		font-size: 22rpx;
		color: #7a6652;
	}

	.table-scroll {
		margin-top: 16rpx;
		white-space: nowrap;
	}

	.table {
		min-width: 860rpx;
	}

	.pair-rating-row {
		padding-top: 12rpx;
	}

	.group-rating-row {
		padding-top: 10rpx;
		padding-bottom: 2rpx;
	}

	.pair-rating-badge {
		display: inline-flex;
		align-items: center;
		height: 42rpx;
		padding: 0 18rpx;
		border-radius: 999rpx;
		font-size: 22rpx;
		font-weight: 600;
	}

	.pair-rating-s {
		color: #7a3f00;
		background: linear-gradient(135deg, #ffe39a, #f7c85c);
	}

	.pair-rating-a {
		color: #7a4a12;
		background: #f6dfbf;
	}

	.pair-rating-b {
		color: #1f6b52;
		background: #d9efe6;
	}

	.pair-rating-c {
		color: #8b5e1a;
		background: #f8ebcf;
	}

	.pair-rating-d {
		color: #8a4e4e;
		background: #f3dddd;
	}

	.table-row {
		display: flex;
		align-items: center;
		padding: 16rpx 0;
		border-bottom: 1rpx solid #efe4d5;
	}

	.detail-row {
		padding: 0 0 20rpx;
		border-bottom: 1rpx solid #efe4d5;
	}

	.table-header {
		padding-top: 0;
		font-size: 22rpx;
		font-weight: 600;
		color: #8c745b;
	}

	.col {
		box-sizing: border-box;
		padding-right: 16rpx;
		font-size: 24rpx;
		color: #2f261e;
	}

	.col-combo {
		width: 220rpx;
	}

	.col-member {
		width: 320rpx;
	}

	.member-cell {
		cursor: pointer;
		padding: 8rpx 12rpx 8rpx 0;
		border-radius: 14rpx;
		transition: all 0.2s ease;
	}

	.member-cell.active {
		background: rgba(31, 107, 82, 0.1);
	}

	.member-link {
		color: #1f6b52;
		font-weight: 600;
	}

	.member-link-male {
		color: #2a6ee8;
	}

	.member-link-female {
		color: #e85f9c;
	}

	.member-detail-card {
		padding: 24rpx;
		border-radius: 20rpx;
		background: #f8f3ea;
		border: 1rpx solid #eadfce;
	}

	.member-detail-head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 16rpx;
	}

	.member-detail-title {
		display: block;
		font-size: 28rpx;
		font-weight: 700;
		color: #2d241c;
	}

	.member-detail-subtitle {
		display: block;
		margin-top: 8rpx;
		font-size: 22rpx;
		color: #7a6652;
	}

	.member-detail-tip {
		display: block;
		margin-top: 12rpx;
		font-size: 21rpx;
		color: #9a8269;
	}

	.member-detail-close {
		font-size: 22rpx;
		color: #8f6840;
	}

	.member-detail-photo {
		display: block;
		width: 160rpx;
		height: 160rpx;
		margin-top: 20rpx;
		border-radius: 18rpx;
		background: #efe5d3;
	}

	.member-detail-grid {
		display: flex;
		flex-wrap: wrap;
		gap: 12rpx 20rpx;
		margin-top: 20rpx;
	}

	.member-detail-item {
		width: calc(50% - 10rpx);
		font-size: 23rpx;
		color: #3c3228;
	}

	.member-detail-block {
		margin-top: 18rpx;
	}

	.member-detail-block-title {
		display: block;
		font-size: 22rpx;
		font-weight: 600;
		color: #8c745b;
	}

	.member-detail-block-text {
		display: block;
		margin-top: 8rpx;
		font-size: 24rpx;
		line-height: 1.7;
		color: #2f261e;
		white-space: pre-wrap;
		word-break: break-all;
	}
</style>
