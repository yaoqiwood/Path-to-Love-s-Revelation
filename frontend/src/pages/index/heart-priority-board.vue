<template>
	<section class="priority-page">
		<section class="priority-shell">
			<div class="priority-glow priority-glow-left"></div>
			<div class="priority-glow priority-glow-right"></div>
			<div class="priority-orbit priority-orbit-top"></div>

			<header class="hero-copy">
				<button class="ghost-btn back-nav-btn" type="button" @click="goBackHome">
					{{ TEXT.backHome }}
				</button>
				<p class="eyebrow">{{ TEXT.eyebrow }}</p>
				<div class="hero-row">
					<div>
						<h1 class="headline">{{ TEXT.title }}</h1>
						<p class="subhead">{{ heroDescription }}</p>
					</div>
				</div>
			</header>
			<section class="workbench">
				<aside class="ranking-panel">
					<div class="panel-head ranking-head">
						<div class="panel-count accent-count">
							当前：{{ selectedCount }}/{{ state.board.limit || 10 }}
						</div>
					</div>

					<p class="ranking-copy">{{ rankingDescription }}</p>

					<div class="ranking-list">
						<article
							v-for="(candidate, index) in selectedList"
							:key="candidate._id"
							class="ranking-item"
						>
							<div class="ranking-index">{{ index + 1 }}</div>
							<div class="ranking-main">
								<div class="ranking-name-row">
									<h4>{{ candidate.nickname || candidate.name }}</h4>
									<span class="ranking-mbti">{{ candidate.mbti }}</span>
								</div>
								<p class="ranking-meta">{{ candidate.profession }} / {{ candidate.city }}</p>
							</div>
							<div class="ranking-actions">
								<button
									class="icon-btn"
									type="button"
									:disabled="index === 0"
									@click="moveCandidate(index, -1)"
								>
									{{ TEXT.moveUp }}
								</button>
								<button
									class="icon-btn"
									type="button"
									:disabled="index === selectedList.length - 1"
									@click="moveCandidate(index, 1)"
								>
									{{ TEXT.moveDown }}
								</button>
								<button
									class="icon-btn danger-btn"
									type="button"
									@click="removeSelected(candidate._id)"
								>
									{{ TEXT.removeShort }}
								</button>
							</div>
						</article>

						<article
							v-for="slot in placeholderSlots"
							:key="'placeholder-' + slot"
							class="ranking-item ranking-placeholder"
						>
							<div class="ranking-index">{{ selectedList.length + slot }}</div>
							<div class="ranking-main">
								<h4>{{ TEXT.placeholderTitle }}</h4>
								<!-- <p class="ranking-meta">{{ TEXT.placeholderCopy }}</p> -->
							</div>
							<button
								class="placeholder-add-btn"
								type="button"
								@click.stop="openCandidatePicker(slot)"
							>
								+
							</button>
						</article>
					</div>

					<div class="action-stack">
						<button
							class="ghost-btn action-btn"
							type="button"
							:disabled="state.loading || state.saving || !hasChanges"
							@click="saveDraft"
						>
							{{ state.saving ? TEXT.saving : TEXT.saveDraft }}
						</button>
						<button
							class="primary-btn action-btn"
							type="button"
							:disabled="
								state.loading || state.saving || selectedCount !== (state.board.limit || 10)
							"
							@click="submitBoard"
						>
							{{ state.saving ? TEXT.submitting : TEXT.submitBoard }}
						</button>
						<button
							class="text-btn"
							type="button"
							:disabled="state.loading || state.saving || !selectedCount"
							@click="resetSelection"
						>
							{{ TEXT.resetBoard }}
						</button>
					</div>
				</aside>
			</section>

			<div
				v-if="state.picker.visible"
				class="picker-modal-mask"
				role="dialog"
				aria-modal="true"
				@click.self="closeCandidatePicker"
			>
				<div class="picker-modal">
					<div class="picker-head">
						<h3>{{ TEXT.pickerTitle }}</h3>
						<p>{{ TEXT.pickerSubtitle }}</p>
					</div>

					<div v-if="!availableOppositeCandidates.length" class="picker-empty">
						{{ TEXT.pickerEmpty }}
					</div>
					<div v-else class="picker-table-wrap">
						<table class="picker-table">
							<thead>
								<tr>
									<th>{{ TEXT.colName }}</th>
									<th>{{ TEXT.colAge }}</th>
									<th>{{ TEXT.colCity }}</th>
									<th>{{ TEXT.colProfession }}</th>
									<th>{{ TEXT.colMbti }}</th>
								</tr>
							</thead>
							<tbody>
								<tr
									v-for="candidate in availableOppositeCandidates"
									:key="'picker-' + candidate._id"
									:class="state.picker.selectedId === candidate._id ? 'is-active' : ''"
									@click="selectCandidateForPicker(candidate._id)"
								>
									<td>
										{{ candidate.name || candidate.nickname || '--' }}
										{{ formatGenderSymbol(candidate.gender) }}
									</td>
									<td>{{ candidate.age || '--' }}</td>
									<td>{{ candidate.city || '--' }}</td>
									<td>{{ candidate.profession || '--' }}</td>
									<td>{{ candidate.mbti || '--' }}</td>
								</tr>
							</tbody>
						</table>
					</div>

					<div class="picker-actions">
						<button class="ghost-btn" type="button" @click="closeCandidatePicker">
							{{ TEXT.pickerBack }}
						</button>
						<button
							class="primary-btn"
							type="button"
							:disabled="!state.picker.selectedId"
							@click="confirmCandidatePicker"
						>
							{{ TEXT.pickerConfirm }}
						</button>
					</div>
				</div>
			</div>
		</section>
	</section>
</template>

<script setup>
	import { computed, reactive } from 'vue'
	import { onLoad } from '@dcloudio/uni-app'
	import { useRouter } from 'vue-router'
	import {
		getLocalUserHeartPriorityBoard,
		getPersonnelList,
		saveLocalUserHeartPriorityBoard,
		submitLocalUserHeartPriorityBoard
	} from '@/api/modules/personnel-user'
	import { app } from '@/platform/app-bridge'

	const PROFILE_KEY = 'mbtiPersonnelProfile'

	const TEXT = {
		eyebrow: 'PATH TO LOVE',
		title: '心动的信号',
		backHome: '返回导航',
		removeShort: '移出',
		moveUp: '上移',
		moveDown: '下移',
		saveDraft: '保存草稿',
		submitBoard: '提交',
		saving: '正在保存...',
		submitting: '正在提交...',
		resetBoard: '清空本次排名',
		placeholderTitle: '尚未选人',
		placeholderCopy: '点击可加入，补齐 10 位即可提交。',
		needLogin: '请先完成登录或档案匹配',
		noAccess: '只有普通用户可以进入心动优先榜',
		loadFailed: '加载失败',
		saveSuccess: '草稿已保存',
		submitSuccess: '心动优先榜已提交',
		topTargetMale: '选出你想了解的10个男生吧！',
		topTargetFemale: '选出你想了解的10个女生吧！',
		pickerTitle: '选择异性候选人',
		pickerSubtitle: '点击一行可选中候选人，确认后将加入当前排名。',
		pickerEmpty: '当前没有可加入的异性候选人。',
		pickerBack: '返回',
		pickerConfirm: '确认加入',
		colName: '姓名',
		colAge: '年龄',
		colCity: '城市',
		colProfession: '职业',
		colMbti: 'MBTI',
		pickerLimitReached: '已选满 10 位，请先移除后再添加。',
		pickerNeedChoose: '请先选择一位候选人。'
	}

	const router = useRouter()

	const state = reactive({
		loading: true,
		saving: false,
		profile: null,
		personnelId: '',
		self: null,
		board: {
			limit: 10,
			status: 'draft',
			selected_ids: [],
			submitted_at: '',
			updated_at: ''
		},
		personnelPool: [],
		candidates: [],
		orderedIds: [],
		savedOrderedIds: [],
		picker: {
			visible: false,
			targetSlot: 0,
			selectedId: ''
		}
	})

	onLoad(async () => {
		await bootstrap()
	})

	const selectedCount = computed(() => state.orderedIds.length)

	const selectedList = computed(() => {
		const candidateMap = state.candidates.reduce((accumulator, item) => {
			const id = getCandidateId(item)
			if (id) {
				accumulator[id] = item
			}
			return accumulator
		}, {})
		return state.orderedIds.map((item) => candidateMap[String(item)]).filter(Boolean)
	})

	const placeholderSlots = computed(() => {
		const total = Math.max(0, (state.board.limit || 10) - selectedCount.value)
		return Array.from({ length: total }, (_, index) => index + 1)
	})

	const heroDescription = computed(() => {
		if (state.self && state.self.priority_target_gender === 'male') {
			return TEXT.topTargetMale
		}
		return TEXT.topTargetFemale
	})

	const rankingDescription = computed(() => {
		if (!selectedCount.value) {
			return '您还未开始选择，点击选择加入，补齐 10 位即可提交。'
		}
		return '可以通过上移、下移调整顺序，第 1 名代表你当下最想进一步了解的人。'
	})

	const hasChanges = computed(
		() => JSON.stringify(state.orderedIds) !== JSON.stringify(state.savedOrderedIds)
	)

	const availableOppositeCandidates = computed(() => {
		const sourceList = state.candidates.length
			? state.candidates
			: buildOppositeCandidates(normalizePersonnelPool(getPersonnelList()), state.self)
		const selectedIdSet = new Set(state.orderedIds.map((item) => String(item)))
		return sourceList.filter((item) => {
			const id = getCandidateId(item)
			return !!id && !selectedIdSet.has(id)
		})
	})

	async function bootstrap() {
		const profile = getStoredProfile()
		const userRole = Number(profile && profile.user_role) || 0
		const personnelId = (profile && (profile.personnel_id || profile._id || profile.id)) || ''

		if (!personnelId) {
			app.showToast({ title: TEXT.needLogin, icon: 'none' })
			goBackHome()
			return
		}

		if (userRole !== 0) {
			app.showToast({ title: TEXT.noAccess, icon: 'none' })
			goBackHome()
			return
		}

		state.profile = profile
		state.personnelId = personnelId
		await loadBoard()
	}

	function getStoredProfile() {
		try {
			const stored = app.getStorageSync(PROFILE_KEY)
			return stored && typeof stored === 'object' ? stored : null
		} catch (error) {
			return null
		}
	}

	async function loadBoard() {
		if (!state.personnelId) {
			return
		}

		state.loading = true
		try {
			state.personnelPool = normalizePersonnelPool(getPersonnelList())
			state.self = resolveSelfRecord(state.personnelId, state.profile, state.personnelPool)
			const result = getLocalUserHeartPriorityBoard({
				personnelId: state.personnelId
			})
			applyBoardResult(result)
		} catch (error) {
			app.showToast({
				title: (error && error.message) || TEXT.loadFailed,
				icon: 'none'
			})
		} finally {
			state.loading = false
		}
	}

	function applyBoardResult(result) {
		state.self = resolveSelfRecord(
			state.personnelId,
			(result && result.self) || state.profile,
			state.personnelPool
		)
		state.board = Object.assign(
			{
				limit: 10,
				status: 'draft',
				selected_ids: [],
				submitted_at: '',
				updated_at: ''
			},
			(result && result.board) || {}
		)
		state.candidates = buildOppositeCandidates(state.personnelPool, state.self)
		state.orderedIds = Array.isArray(state.board.selected_ids)
			? state.board.selected_ids.map((item) => String(item))
			: []
		state.savedOrderedIds = [...state.orderedIds]
		closeCandidatePicker()
	}

	function resolveSelfRecord(personnelId, fallbackSelf, personnelPool) {
		const normalizedPersonnelId = String(personnelId || '')
		const fromPool = (Array.isArray(personnelPool) ? personnelPool : []).find(
			(item) => getCandidateId(item) === normalizedPersonnelId
		)
		return fromPool || fallbackSelf || null
	}

	function moveCandidate(index, delta) {
		const nextIndex = index + delta
		if (index < 0 || nextIndex < 0 || nextIndex >= state.orderedIds.length) {
			return
		}

		const nextOrderedIds = [...state.orderedIds]
		const currentItem = nextOrderedIds[index]
		nextOrderedIds[index] = nextOrderedIds[nextIndex]
		nextOrderedIds[nextIndex] = currentItem
		state.orderedIds = nextOrderedIds
	}

	function removeSelected(id) {
		state.orderedIds = state.orderedIds.filter((item) => item !== id)
	}

	function openCandidatePicker(slot) {
		if (state.loading || state.saving) {
			return
		}

		const limit = state.board.limit || 10
		if (state.orderedIds.length >= limit) {
			app.showToast({ title: TEXT.pickerLimitReached, icon: 'none' })
			return
		}

		state.picker.visible = true
		state.picker.targetSlot = Number(slot) || 0
		state.picker.selectedId = ''
	}

	function closeCandidatePicker() {
		state.picker.visible = false
		state.picker.targetSlot = 0
		state.picker.selectedId = ''
	}

	function selectCandidateForPicker(candidateId) {
		state.picker.selectedId = String(candidateId || '')
	}

	function confirmCandidatePicker() {
		const candidateId = state.picker.selectedId
		if (!candidateId) {
			app.showToast({ title: TEXT.pickerNeedChoose, icon: 'none' })
			return
		}

		if (state.orderedIds.includes(candidateId)) {
			closeCandidatePicker()
			return
		}

		const limit = state.board.limit || 10
		if (state.orderedIds.length >= limit) {
			app.showToast({ title: TEXT.pickerLimitReached, icon: 'none' })
			return
		}

		state.orderedIds.push(candidateId)
		closeCandidatePicker()
	}

	async function saveDraft() {
		if (!state.personnelId || state.saving) {
			return
		}

		state.saving = true
		try {
			const result = saveLocalUserHeartPriorityBoard({
				personnelId: state.personnelId,
				orderedIds: state.orderedIds
			})
			applyBoardResult(result)
			app.showToast({ title: TEXT.saveSuccess, icon: 'success' })
		} catch (error) {
			app.showToast({
				title: (error && error.message) || TEXT.loadFailed,
				icon: 'none'
			})
		} finally {
			state.saving = false
		}
	}

	async function submitBoard() {
		if (!state.personnelId || state.saving) {
			return
		}

		const limit = state.board.limit || 10
		if (state.orderedIds.length !== limit) {
			app.showToast({
				title: '请先选满 10 位候选人再提交。',
				icon: 'none'
			})
			return
		}

		state.saving = true
		try {
			const result = submitLocalUserHeartPriorityBoard({
				personnelId: state.personnelId,
				orderedIds: state.orderedIds
			})
			applyBoardResult(result)
			app.showToast({ title: TEXT.submitSuccess, icon: 'success' })
		} catch (error) {
			app.showToast({
				title: (error && error.message) || TEXT.loadFailed,
				icon: 'none'
			})
		} finally {
			state.saving = false
		}
	}

	function resetSelection() {
		state.orderedIds = []
	}

	function goBackHome() {
		router.push('/pages/index/home')
	}

	function getCandidateId(candidate) {
		if (!candidate || typeof candidate !== 'object') {
			return ''
		}
		return String(
			candidate._id ||
				candidate.id ||
				candidate.personnel_id ||
				candidate.person_id ||
				candidate.candidate_id ||
				''
		)
	}

	function normalizePersonnelPool(source) {
		if (!Array.isArray(source)) {
			return []
		}
		return source.filter(Boolean)
	}

	function buildOppositeCandidates(personnelPool, selfRecord) {
		const selfId = getCandidateId(selfRecord)
		const selfGender = normalizeGender(
			(selfRecord && (selfRecord.gender || selfRecord.sex || selfRecord.user_gender)) || ''
		)
		const list = Array.isArray(personnelPool) ? personnelPool : []

		return list
			.filter((item) => {
				const id = getCandidateId(item)
				if (!id || id === selfId) {
					return false
				}

				if (!selfGender) {
					return true
				}

				const candidateGender = normalizeGender(
					item.gender || item.sex || item.user_gender || item.person_gender || ''
				)
				return !!candidateGender && candidateGender !== selfGender
			})
			.map((item) => ({
				...item,
				_id: getCandidateId(item),
				name: item.name || '',
				nickname: item.nickname || item.name || '',
				age: item.age || '',
				mbti: item.mbti || '',
				city: item.city || item.native_place || item.address || '',
				profession: item.profession || '',
				gender: item.gender || '',
				personal_photo: item.personal_photo || ''
			}))
	}

	function formatGenderSymbol(value) {
		const normalized = normalizeGender(value)
		if (normalized === 'male') {
			return ' ♂'
		}
		if (normalized === 'female') {
			return ' ♀'
		}
		return ''
	}

	function normalizeGender(value) {
		const text = String(value || '')
			.trim()
			.toLowerCase()
		if (!text) {
			return ''
		}
		if (
			text === 'male' ||
			text === 'm' ||
			text === '1' ||
			text === '男' ||
			text === '男生' ||
			text === 'man'
		) {
			return 'male'
		}
		if (
			text === 'female' ||
			text === 'f' ||
			text === '0' ||
			text === '2' ||
			text === '女' ||
			text === '女生' ||
			text === 'woman'
		) {
			return 'female'
		}
		return ''
	}
</script>

<style scoped lang="less">
	.priority-page {
		--page-ink: #281f1b;
		--page-copy: #695851;
		--page-soft: #8b766d;
		--page-line: rgba(112, 84, 66, 0.12);
		--page-panel: rgba(255, 255, 255, 0.82);
		--page-panel-strong: rgba(255, 255, 255, 0.92);
		--accent-deep: #2d3851;
		--accent-warm: #dd7b56;
		--accent-soft: #fff1e9;
		min-height: 100vh;
		background:
			radial-gradient(circle at 12% 14%, rgba(255, 207, 170, 0.42), transparent 24%),
			radial-gradient(circle at 88% 20%, rgba(148, 203, 255, 0.28), transparent 24%),
			linear-gradient(180deg, #fffdf9 0%, #fff4ec 48%, #fffaf5 100%);
	}

	.priority-shell {
		position: relative;
		min-height: 100vh;
		max-width: 1420px;
		margin: 0 auto;
		padding: 5px clamp(18px, 4vw, 40px) calc(40px + var(--safe-bottom, 0px));
		overflow: hidden;
	}

	.priority-glow,
	.priority-orbit {
		position: absolute;
		pointer-events: none;
	}

	.priority-glow {
		border-radius: 999px;
		filter: blur(22px);
	}

	.priority-glow-left {
		top: 28px;
		left: -86px;
		width: 220px;
		height: 220px;
		background: rgba(255, 184, 142, 0.38);
	}

	.priority-glow-right {
		top: 170px;
		right: -90px;
		width: 240px;
		height: 240px;
		background: rgba(132, 195, 255, 0.28);
	}

	.priority-orbit-top {
		top: -110px;
		left: 50%;
		width: min(92vw, 880px);
		height: 300px;
		margin-left: calc(min(92vw, 880px) / -2);
		border-radius: 50%;
		background:
			radial-gradient(circle at center, rgba(255, 255, 255, 0.82), transparent 64%),
			linear-gradient(180deg, rgba(255, 237, 226, 0.64), rgba(255, 255, 255, 0));
	}

	.hero-copy,
	.summary-grid,
	.story-card,
	.workbench {
		position: relative;
		z-index: 2;
	}

	.hero-copy {
		padding-top: 54px;
	}

	.eyebrow,
	.panel-kicker,
	.story-kicker,
	.summary-label {
		margin: 0;
		color: #8d6450;
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.24em;
		text-transform: uppercase;
	}

	.hero-row,
	.story-head,
	.panel-head,
	.progress-head,
	.status-row,
	.candidate-top,
	.candidate-actions,
	.ranking-name-row,
	.ranking-item,
	.ranking-actions,
	.summary-grid {
		display: flex;
	}

	.hero-row,
	.story-head,
	.panel-head,
	.status-row,
	.candidate-actions,
	.ranking-item {
		align-items: center;
		justify-content: space-between;
		gap: 16px;
	}

	.hero-row {
		justify-content: flex-start;
	}

	.headline {
		margin: 14px 0 0;
		color: var(--page-ink);
		font-family: var(--font-display);
		font-size: clamp(40px, 5vw, 64px);
		line-height: 1.04;
	}

	.subhead {
		max-width: 34em;
		margin: 16px 0 0;
		color: var(--page-copy);
		font-size: 16px;
		line-height: 1.8;
	}

	.summary-grid {
		gap: 16px;
		margin-top: 26px;
	}

	.summary-card,
	.story-card,
	.candidate-panel,
	.ranking-panel {
		border: 1px solid var(--page-line);
		border-radius: 30px;
		background:
			linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(255, 247, 241, 0.8)),
			var(--page-panel);
		box-shadow:
			0 24px 44px rgba(117, 88, 63, 0.1),
			inset 0 1px 0 rgba(255, 255, 255, 0.72);
		backdrop-filter: blur(18px);
	}

	.summary-card {
		flex: 1;
		min-width: 0;
		padding: 22px 24px;
	}

	.summary-card-identity {
		flex: 1.1;
		background:
			linear-gradient(135deg, rgba(46, 55, 79, 0.96), rgba(73, 84, 111, 0.92)),
			rgba(35, 43, 62, 0.92);
		color: #fff8f2;
	}

	.summary-card-identity .summary-label,
	.summary-card-identity .summary-copy,
	.summary-card-identity .summary-value {
		color: #fff8f2;
	}
	.summary-value {
		margin: 10px 0 0;
		font-size: 30px;
		line-height: 1.15;
		color: var(--page-ink);
	}

	.summary-copy {
		margin: 12px 0 0;
		color: var(--page-copy);
		font-size: 14px;
		line-height: 1.7;
	}

	.progress-head strong {
		font-size: 34px;
		color: var(--page-ink);
	}

	.progress-head span,
	.status-meta,
	.panel-count,
	.candidate-meta,
	.candidate-role,
	.candidate-church,
	.ranking-meta {
		color: var(--page-soft);
		font-size: 13px;
	}

	.progress-track {
		margin-top: 14px;
		height: 12px;
		border-radius: 999px;
		background: rgba(45, 56, 81, 0.1);
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		border-radius: inherit;
		background: linear-gradient(90deg, var(--accent-warm) 0%, var(--accent-deep) 100%);
		box-shadow: 0 12px 22px rgba(45, 56, 81, 0.2);
	}

	.status-pill,
	.story-badge,
	.rank-pill,
	.tag-chip,
	.ranking-mbti,
	.filter-chip {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		border-radius: 999px;
		white-space: nowrap;
	}

	.status-pill {
		min-height: 34px;
		padding: 0 14px;
		font-size: 13px;
		font-weight: 700;
	}

	.status-pill.is-draft {
		background: rgba(255, 232, 214, 0.96);
		color: #9d5d39;
	}

	.status-pill.is-submitted {
		background: rgba(223, 241, 230, 0.96);
		color: #2f7a4e;
	}

	.story-card {
		margin-top: 18px;
		padding: 24px 26px;
	}

	.story-title {
		margin: 12px 0 0;
		color: var(--page-ink);
		font-size: clamp(28px, 3vw, 36px);
		line-height: 1.12;
	}

	.story-copy {
		margin: 14px 0 0;
		color: var(--page-copy);
		font-size: 15px;
		line-height: 1.8;
	}

	.story-badge {
		min-height: 42px;
		padding: 0 16px;
		background: rgba(45, 56, 81, 0.08);
		color: var(--accent-deep);
		font-size: 13px;
		font-weight: 700;
	}

	.workbench {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: 18px;
		margin-top: 20px;
		align-items: start;
	}

	.ranking-panel {
		padding: 24px;
	}

	.panel-title {
		margin: 10px 0 0;
		color: var(--page-ink);
		font-size: 28px;
		line-height: 1.15;
	}

	.panel-count {
		min-width: 74px;
		text-align: left;
	}

	.accent-count {
		color: var(--accent-deep);
		font-weight: 700;
	}

	.toolbar {
		margin-top: 18px;
	}

	.search-shell {
		display: flex;
		align-items: center;
		gap: 10px;
		min-height: 56px;
		padding: 0 18px;
		border-radius: 20px;
		background: rgba(255, 255, 255, 0.94);
		border: 1px solid rgba(112, 84, 66, 0.1);
		box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.76);
	}

	.search-icon {
		color: #9a7668;
		font-size: 18px;
	}

	.search-input {
		width: 100%;
		min-width: 0;
		border: none;
		background: transparent;
		color: var(--page-ink);
		font-size: 15px;
		outline: none;
	}

	.filter-row {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		margin-top: 14px;
	}

	.filter-chip {
		min-height: 40px;
		padding: 0 14px;
		border: 1px solid rgba(112, 84, 66, 0.08);
		background: rgba(255, 255, 255, 0.84);
		color: #735f55;
		font-size: 13px;
		font-weight: 700;
	}

	.filter-chip.is-active {
		background: linear-gradient(135deg, rgba(45, 56, 81, 0.96), rgba(84, 98, 136, 0.92));
		color: #fff8f1;
	}

	.panel-empty {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 260px;
		margin-top: 18px;
		border-radius: 24px;
		border: 1px dashed rgba(112, 84, 66, 0.16);
		color: var(--page-soft);
		font-size: 14px;
		text-align: center;
		background: rgba(255, 255, 255, 0.52);
	}

	.candidate-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 16px;
		margin-top: 18px;
	}

	.candidate-card {
		padding: 18px;
		border-radius: 24px;
		border: 1px solid rgba(112, 84, 66, 0.08);
		background:
			linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(255, 249, 244, 0.92)),
			rgba(255, 255, 255, 0.94);
		box-shadow: 0 18px 30px rgba(117, 88, 63, 0.08);
	}

	.candidate-card.is-selected {
		border-color: rgba(45, 56, 81, 0.18);
		box-shadow: 0 24px 38px rgba(45, 56, 81, 0.12);
	}

	.avatar-shell {
		flex-shrink: 0;
		width: 68px;
		height: 68px;
		border-radius: 20px;
		overflow: hidden;
		background: linear-gradient(180deg, #f7dfd4 0%, #dbe8fb 100%);
	}

	.avatar,
	.avatar-fallback {
		width: 100%;
		height: 100%;
	}

	.avatar-fallback {
		display: flex;
		align-items: center;
		justify-content: center;
		color: #fff7ef;
		font-size: 20px;
		font-weight: 700;
		letter-spacing: 0.08em;
		background: linear-gradient(135deg, #d97854 0%, #576386 100%);
	}

	.candidate-main {
		flex: 1;
		min-width: 0;
	}

	.candidate-name-row,
	.ranking-name-row {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.candidate-name-row h4,
	.ranking-main h4 {
		margin: 0;
		color: var(--page-ink);
		font-size: 20px;
		line-height: 1.15;
	}

	.rank-pill {
		min-height: 30px;
		padding: 0 10px;
		background: rgba(45, 56, 81, 0.1);
		color: var(--accent-deep);
		font-size: 12px;
		font-weight: 700;
	}

	.candidate-meta,
	.candidate-role,
	.candidate-intro,
	.ranking-copy,
	.ranking-meta,
	.candidate-church {
		margin: 10px 0 0;
		line-height: 1.65;
	}

	.candidate-intro,
	.ranking-copy {
		color: var(--page-copy);
		font-size: 14px;
	}

	.tag-row {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		margin-top: 14px;
	}

	.tag-chip,
	.ranking-mbti {
		min-height: 30px;
		padding: 0 10px;
		background: rgba(255, 240, 228, 0.84);
		color: #8a5e49;
		font-size: 12px;
		font-weight: 700;
	}

	.candidate-actions {
		margin-top: 16px;
	}

	.primary-btn,
	.ghost-btn,
	.icon-btn,
	.text-btn {
		border: none;
		cursor: pointer;
	}

	.primary-btn,
	.ghost-btn {
		min-height: 52px;
		padding: 0 22px;
		border-radius: 999px;
		font-size: 15px;
		font-weight: 700;
	}

	.primary-btn {
		background: linear-gradient(135deg, #2d3851 0%, #4f638e 100%);
		color: #fff9f1;
		box-shadow: 0 16px 28px rgba(45, 56, 81, 0.18);
	}

	.ghost-btn {
		background: rgba(255, 255, 255, 0.84);
		color: #4f3c35;
		border: 1px solid rgba(112, 84, 66, 0.1);
	}

	.compact-btn {
		flex-shrink: 0;
		min-height: 48px;
	}

	.back-nav-btn {
		position: absolute;
		top: 0;
		left: 0;
		min-height: 36px;
		padding: 0 14px;
		font-size: 12px;
		line-height: 1;
		border-radius: 999px;
		z-index: 3;
	}

	.small-btn {
		min-height: 42px;
		padding: 0 16px;
		font-size: 13px;
	}

	.primary-btn:disabled,
	.ghost-btn:disabled,
	.icon-btn:disabled,
	.text-btn:disabled {
		cursor: not-allowed;
		opacity: 0.56;
		box-shadow: none;
	}

	.ranking-panel {
		position: sticky;
		top: calc(18px + var(--safe-top, 0px));
		background:
			linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(247, 241, 236, 0.92)),
			var(--page-panel-strong);
	}

	.ranking-copy {
		margin-top: 16px;
	}

	.ranking-list {
		display: grid;
		gap: 12px;
		margin-top: 18px;
		max-height: min(58vh, 560px);
		overflow-y: auto;
		overflow-x: hidden;
		padding-right: 4px;
	}

	.ranking-item {
		padding: 16px;
		border-radius: 22px;
		border: 1px solid rgba(112, 84, 66, 0.08);
		background: rgba(255, 255, 255, 0.88);
		align-items: flex-start;
	}

	.ranking-placeholder {
		background: rgba(255, 255, 255, 0.55);
		border-style: dashed;
		transition:
			border-color 0.2s ease,
			background-color 0.2s ease;
	}

	.ranking-placeholder:hover {
		border-color: rgba(45, 56, 81, 0.34);
		background: rgba(236, 243, 255, 0.78);
	}

	.placeholder-add-btn {
		width: 34px;
		min-width: 34px;
		height: 34px;
		border: 1px solid rgba(45, 56, 81, 0.26);
		border-radius: 50%;
		background: rgba(45, 56, 81, 0.06);
		color: var(--accent-deep);
		font-size: 24px;
		line-height: 1;
		font-weight: 500;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		flex-shrink: 0;
	}

	.placeholder-add-btn:hover {
		background: rgba(45, 56, 81, 0.12);
	}

	.ranking-index {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 38px;
		min-width: 38px;
		height: 38px;
		border-radius: 50%;
		background: rgba(45, 56, 81, 0.1);
		color: var(--accent-deep);
		font-weight: 700;
	}

	.ranking-main {
		flex: 1;
		min-width: 0;
		padding: 2px 0 0;
	}

	.ranking-actions {
		flex-wrap: wrap;
		justify-content: flex-end;
		gap: 8px;
	}

	.icon-btn {
		min-height: 34px;
		padding: 0 12px;
		border-radius: 999px;
		background: rgba(45, 56, 81, 0.08);
		color: var(--accent-deep);
		font-size: 12px;
		font-weight: 700;
	}

	.danger-btn {
		background: rgba(240, 102, 70, 0.12);
		color: #bf4f31;
	}

	.action-stack {
		display: grid;
		gap: 10px;
		margin-top: 18px;
	}

	.action-btn {
		width: 100%;
	}

	.text-btn {
		min-height: 40px;
		background: transparent;
		color: #8a6557;
		font-size: 13px;
		font-weight: 700;
	}

	.picker-modal-mask {
		position: fixed;
		inset: 0;
		z-index: 40;
		display: grid;
		place-items: center;
		padding: 18px;
		background: rgba(30, 25, 22, 0.42);
		backdrop-filter: blur(3px);
	}

	.picker-modal {
		width: min(960px, 100%);
		max-height: min(86vh, 760px);
		display: grid;
		grid-template-rows: auto minmax(0, 1fr) auto;
		gap: 14px;
		padding: 20px;
		border-radius: 22px;
		border: 1px solid rgba(112, 84, 66, 0.16);
		background: #fffdfa;
		box-shadow: 0 24px 44px rgba(25, 20, 17, 0.26);
	}

	.picker-head h3 {
		margin: 0;
		color: var(--page-ink);
		font-size: 22px;
	}

	.picker-head p {
		margin: 8px 0 0;
		color: var(--page-soft);
		font-size: 13px;
		line-height: 1.6;
	}

	.picker-empty {
		display: grid;
		place-items: center;
		min-height: 180px;
		color: var(--page-soft);
		font-size: 14px;
		border: 1px dashed rgba(112, 84, 66, 0.2);
		border-radius: 14px;
		background: rgba(255, 255, 255, 0.7);
	}

	.picker-table-wrap {
		height: min(52vh, 460px);
		overflow-x: auto;
		overflow-y: auto;
		border-radius: 14px;
		border: 1px solid rgba(112, 84, 66, 0.14);
		scrollbar-width: none;
		-ms-overflow-style: none;

		&::-webkit-scrollbar {
			width: 0;
			height: 0;
		}

		&:hover,
		&:active {
			scrollbar-width: thin;
			scrollbar-color: rgba(112, 84, 66, 0.32) rgba(112, 84, 66, 0.08);
		}

		&:hover::-webkit-scrollbar,
		&:active::-webkit-scrollbar {
			width: 8px;
			height: 8px;
		}

		&:hover::-webkit-scrollbar-track,
		&:active::-webkit-scrollbar-track {
			background: rgba(112, 84, 66, 0.08);
			border-radius: 4px;
		}

		&:hover::-webkit-scrollbar-thumb,
		&:active::-webkit-scrollbar-thumb {
			background: rgba(112, 84, 66, 0.32);
			border-radius: 4px;
		}
	}

	.picker-table {
		width: 100%;
		border-collapse: collapse;
		background: #fff;
	}

	.picker-table th,
	.picker-table td {
		padding: 11px 12px;
		text-align: left;
		font-size: 13px;
		border-bottom: 1px solid rgba(112, 84, 66, 0.08);
		white-space: nowrap;
	}

	.picker-table td:first-child {
		max-width: 150px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.picker-table th {
		position: sticky;
		top: 0;
		z-index: 1;
		background: #fff5ef;
		color: #71554a;
		font-weight: 700;
	}

	.picker-table tbody tr {
		cursor: pointer;
		transition: background-color 0.15s ease;
	}

	.picker-table tbody tr:hover {
		background: #fff3ea;
	}

	.picker-table tbody tr.is-active {
		background: #eaf2ff;
	}

	.picker-actions {
		display: flex;
		justify-content: flex-end;
		gap: 10px;
	}

	@media (max-width: 1180px) {
		.workbench {
			grid-template-columns: 1fr;
		}

		.ranking-panel {
			position: relative;
			top: auto;
		}
	}

	@media (max-width: 900px) {
		.summary-grid {
			flex-direction: column;
		}

		.candidate-grid {
			grid-template-columns: 1fr;
		}
	}

	@media (max-width: 640px) {
		.priority-shell {
			padding-left: 16px;
			padding-right: 16px;
		}

		.hero-row,
		.story-head,
		.panel-head,
		.candidate-top,
		.candidate-actions,
		.ranking-item {
			flex-direction: column;
			align-items: flex-start;
		}

		.compact-btn,
		.primary-btn,
		.ghost-btn {
			width: 100%;
		}

		.ranking-actions {
			width: 100%;
			justify-content: flex-start;
		}

		.ranking-item.ranking-placeholder {
			flex-direction: row;
			align-items: center;
		}

		.back-nav-btn {
			width: auto;
		}

		.ranking-list {
			max-height: 52vh;
		}

		.picker-actions {
			flex-direction: column;
		}

		.picker-actions .ghost-btn,
		.picker-actions .primary-btn {
			width: 100%;
		}
	}
</style>

