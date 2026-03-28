<template>
	<view class="page">
		<view class="hero">
			<view class="hero-backdrop hero-backdrop-left"></view>
			<view class="hero-backdrop hero-backdrop-right"></view>

			<view class="hero-copy">
				<text class="eyebrow">LOVE MBTI LAB</text>
				<text class="headline">{{ pageTitle }}</text>
				<text class="subhead">{{ pageSubtitle }}</text>
			</view>

			<view class="progress-card">
				<view class="progress-meta">
					<text class="progress-title">答题进度</text>
					<text class="progress-count">{{ answeredCount }}/{{ totalQuestions }}</text>
				</view>
				<view class="progress-track">
					<view class="progress-fill" :style="{ width: `${progressPercent}%` }"></view>
				</view>
				<view class="stage-row">
					<view
						v-for="(stage, index) in stageList"
						:key="stage.label"
						class="stage-pill"
						:class="getStageClass(index)"
					>
						<text class="stage-index">{{ formatStageIndex(index + 1) }}</text>
						<text class="stage-label">{{ stage.label }}</text>
					</view>
				</view>
			</view>

			<view v-if="showStageSummary" class="summary-card">
				<text class="card-eyebrow">STAGE CHECKPOINT</text>
				<text class="summary-title">{{ stageSummary.title }}</text>
				<text class="summary-copy">{{ stageSummary.description }}</text>

				<view class="summary-portrait">
					<text class="summary-portrait-label">阶段画像</text>
					<text class="summary-portrait-copy">{{ stageSummary.personalityDescription }}</text>
				</view>

				<view class="summary-chip-row">
					<view v-for="item in stageSummary.badges" :key="item" class="summary-chip">
						<text>{{ item }}</text>
					</view>
				</view>

				<text class="summary-encourage">{{ stageSummary.encouragement }}</text>

				<view class="action-btn primary-btn" @click="continueToNextStage">
					<text>{{ pendingStageNumber === stageList.length ? '查看最终结果' : '继续答题' }}</text>
				</view>
			</view>

			<view v-else-if="showResult" class="result-card">
				<text class="card-eyebrow">FINAL RESULT</text>
				<text class="result-type">{{ resultType }}</text>
				<text class="result-copy">{{ resultSummary }}</text>

				<view class="result-chip-row">
					<view v-for="item in resultKeywords" :key="item" class="summary-chip accent-chip">
						<text>{{ item }}</text>
					</view>
				</view>

				<view class="trait-list">
					<view v-for="trait in resultTraits" :key="trait.axis" class="trait-item">
						<view class="trait-meta">
							<text class="trait-axis">{{ trait.axis }}</text>
							<text class="trait-score">{{ trait.leftCount }} : {{ trait.rightCount }}</text>
						</view>
						<view class="trait-track">
							<view class="trait-half trait-left"></view>
							<view class="trait-half trait-right"></view>
							<view
								class="trait-fill"
								:class="trait.dominant === trait.right ? 'fill-right' : 'fill-left'"
								:style="{ width: `${trait.fillWidth}%` }"
							></view>
						</view>
						<text class="trait-note">
							更偏向 {{ trait.dominant }} · {{ trait.dominantPercent }}%
						</text>
					</view>
				</view>

				<view class="result-actions">
					<view class="action-btn ghost-btn" @click="goHome">
						<text>返回首页</text>
					</view>
				</view>
			</view>

			<view v-else class="question-card" :class="{ locked: isTransitioning }">
				<view class="question-meta">
					<text class="question-index">Q{{ currentIndex + 1 }}</text>
					<!-- <text class="question-type">{{ currentQuestion.type }} 维度</text> -->
				</view>

				<text class="question-title">{{ currentQuestion.title }}</text>
				<text class="question-caption">选择更接近你真实状态的一项</text>

				<view class="option-list">
					<view
						v-for="option in currentQuestion.selections"
						:key="`${currentQuestion.id}-${option.dimension}`"
						class="option-card"
						:class="{ selected: selectedDimension === option.dimension }"
						@click="selectOption(option)"
					>
						<view class="option-head">
							<!-- <text class="option-dimension">{{ option.dimension }}</text> -->
							<!-- <text class="option-tip">点击选择</text> -->
						</view>
						<text class="option-text">{{ option.text }}</text>
					</view>
				</view>

				<view class="feedback-panel">
					<text class="feedback-title">{{ liveHintTitle }}</text>
					<text class="feedback-copy">{{ liveHintCopy }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
	import { computed, reactive, ref } from 'vue'
	import { onLoad } from '@dcloudio/uni-app'
	import questionsSource from '@/data/mbti-88-questions.json'
	import { personnelUserService as personnelUser } from '@/api/modules/personnel-user'
	import { getCurrentUserInfo } from '@/platform/app-runtime'

	const questions = questionsSource.questions || []
	const totalQuestions = questions.length
	const stageSize = totalQuestions / 4

	const stageList = [
		{
			label: '初始感知',
			start: 0,
			end: stageSize,
			prompt: '先按第一直觉作答，不要想太久。',
			encouragement: '你已经完成热身阶段，继续答题，轮廓会更清晰。'
		},
		{
			label: '关系线索',
			start: stageSize,
			end: stageSize * 2,
			prompt: '这一段会更明显地拉开你的关系偏好。',
			encouragement: '你的偏好已经开始稳定，继续把细节补充完整。'
		},
		{
			label: '决策倾向',
			start: stageSize * 2,
			end: stageSize * 3,
			prompt: '继续保持真实选择，不要按理想中的自己去回答。',
			encouragement: '还差最后一个阶段，你的结果已经很接近成型。'
		},
		{
			label: '节奏定型',
			start: stageSize * 3,
			end: totalQuestions,
			prompt: '最后一段会决定你在关系节奏中的整体走向。',
			encouragement: '四个阶段都已完成，下一步就能看到完整测试结果。'
		}
	]

	const axisPairs = [
		{
			left: 'E',
			right: 'I',
			label: '社交能量',
			badgeLeft: '更愿意主动表达',
			badgeRight: '更偏向慢热观察',
			sentenceLeft: '更愿意先打开话题、带动互动',
			sentenceRight: '更偏向先观察氛围，在舒服的节奏里慢慢靠近'
		},
		{
			left: 'S',
			right: 'N',
			label: '关注重点',
			badgeLeft: '更看重现实细节',
			badgeRight: '更容易留意未来可能',
			sentenceLeft: '更容易被真实、稳定、能落地的细节打动',
			sentenceRight: '更容易被想法、潜力和未来感吸引'
		},
		{
			left: 'T',
			right: 'F',
			label: '判断方式',
			badgeLeft: '会先理清逻辑',
			badgeRight: '会先照顾感受',
			sentenceLeft: '遇到分歧时会先梳理问题本身和解决路径',
			sentenceRight: '遇到分歧时会先感受彼此有没有被理解和接住'
		},
		{
			left: 'J',
			right: 'P',
			label: '相处节奏',
			badgeLeft: '更希望稳定推进',
			badgeRight: '更希望保留弹性',
			sentenceLeft: '在关系推进上更喜欢清晰、稳定、慢慢落地',
			sentenceRight: '在关系推进上更希望保留空间，让互动自然生长'
		}
	]

	const dimensionKeywords = {
		E: '外向表达',
		I: '内向沉浸',
		S: '现实感知',
		N: '未来想象',
		T: '理性判断',
		F: '情感判断',
		J: '规划节奏',
		P: '开放节奏'
	}

	const stageDescriptionTemplates = [
		({ intro, stageAnsweredCount, stageQuota, stageType, topText, axisText }) =>
			`${intro}这一轮你已经走完本阶段 ${stageAnsweredCount}/${stageQuota} 题，当前浮现出的关系轮廓更像 ${stageType}。最常出现的维度集中在 ${topText || '暂无明显倾向'}。${axisText}`,
		({ intro, stageAnsweredCount, stageQuota, stageType, topText, axisText }) =>
			`${intro}到了这一段末尾，你在本阶段完成了 ${stageAnsweredCount}/${stageQuota} 题，偏好开始从零散选择慢慢收束，临时类型更接近 ${stageType}。眼下出现频率更高的是 ${topText || '暂无明显倾向'}。${axisText}`,
		({ intro, stageAnsweredCount, stageQuota, stageType, topText, axisText }) =>
			`${intro}这一阶段的题目已经答完 ${stageAnsweredCount}/${stageQuota} 题，你的判断方式正在变得更有连续性，目前呈现出的阶段类型偏向 ${stageType}。从作答分布来看，${topText || '各维度暂时比较平均'} 更突出。${axisText}`,
		({ intro, stageAnsweredCount, stageQuota, stageType, topText, axisText }) =>
			`${intro}最后这一段也已经记录了 ${stageAnsweredCount}/${stageQuota} 题，本阶段给出的信号已经足够拼出一版较完整的关系画像，当前阶段类型落在 ${stageType}。在具体维度上，${topText || '整体仍比较均衡'} 更显眼。${axisText}`
	]

	const stageAxisSummaryTemplates = [
		({ strongestAxis, strengthWord }) =>
			`其中在${strongestAxis.label}上，你${strengthWord}偏向 ${strongestAxis.dominant}（${strongestAxis.left}:${strongestAxis.right} = ${strongestAxis.leftCount}:${strongestAxis.rightCount}）。`,
		({ strongestAxis, strengthWord }) =>
			`尤其是${strongestAxis.label}这一组，已经能看出你更靠近 ${strongestAxis.dominant}，而且这种倾向${strengthWord}（${strongestAxis.leftCount}:${strongestAxis.rightCount}）。`,
		({ strongestAxis, strengthWord }) =>
			`如果只看最醒目的一条线索，${strongestAxis.label}目前最能说明你的选择方向，你暂时更站在 ${strongestAxis.dominant} 这一侧，力度算是${strengthWord}。`,
		({ strongestAxis, strengthWord }) =>
			`临近这一阶段收尾时，${strongestAxis.label}给出的信号最清楚：你更偏向 ${strongestAxis.dominant}，比分是 ${strongestAxis.leftCount}:${strongestAxis.rightCount}，倾向已经${strengthWord}。`
	]

	const stageEncouragementTemplates = [
		{
			balanced: (stage) => `${stage.encouragement} 这一段还保留着一些摇摆感，继续按直觉选，后面的轮廓会自然拉开。`,
			leaning: (stage, strongestAxis) =>
				`${stage.encouragement} 你在“${strongestAxis.label}”上已经开始偏向一侧，接下来可以看看这种感觉会不会继续加深。`
		},
		{
			balanced: (stage) => `${stage.encouragement} 目前几组维度咬得很紧，这反而说明你的选择很真实，不用刻意放大某一种样子。`,
			leaning: (stage, strongestAxis) =>
				`${stage.encouragement} 到了这里，“${strongestAxis.label}”已经成为比较稳定的一条线索，后面的题目会帮你把它再确认一次。`
		},
		{
			balanced: (stage) => `${stage.encouragement} 现在的你更像是在几个方向之间细细权衡，最后一段往往最能把这种细微差别说清楚。`,
			leaning: (stage, strongestAxis) =>
				`${stage.encouragement} 这一阶段里，“${strongestAxis.label}”的偏好已经不只是偶然冒头了，最后几题会决定它是短暂信号还是核心特征。`
		},
		{
			balanced: (stage) => `${stage.encouragement} 整体来看你不是单一类型的直线答案，而是带着几分平衡感，这会让最终结果更立体。`,
			leaning: (stage, strongestAxis) =>
				`${stage.encouragement} 回看整段作答，“${strongestAxis.label}”始终是最清楚的一条主线，最终结果大概率也会保留这份底色。`
		}
	]

	const stagePersonalityTemplates = [
		({ social, focus, decision, rhythm }) =>
			`你在人际互动里${social}；在关注一个人或一段关系时，${focus}；${decision}；整体相处节奏上，${rhythm}。`,
		({ social, focus, decision, rhythm }) =>
			`从这一阶段的回答来看，你多半会先以这样的方式进入关系：${social}。真正被你看见的往往是那些${focus}的部分；碰到判断和选择时，${decision}；至于相处节奏，你更像是${rhythm}。`,
		({ social, focus, decision, rhythm }) =>
			`这一轮呈现出的你，像是一个会这样靠近关系的人：${social}，也会${focus}。面对问题时，你通常${decision}；而在推进关系这件事上，你大多${rhythm}。`,
		({ social, focus, decision, rhythm }) =>
			`如果把这一阶段的你写成一张关系侧写，大概会是这样：${social}；你常常${focus}；遇到分歧或需要决定时，${decision}；放到长期相处里，则更倾向于${rhythm}。`
	]

	const typeHeadlines = {
		INTJ: '你会先看整体方向，再决定关系值不值得继续投入。',
		INTP: '你在关系里很重视精神交流和自由空间。',
		ENTJ: '你倾向主动推动关系向更明确的方向发展。',
		ENTP: '你容易被新鲜感、思想碰撞和可能性吸引。',
		INFJ: '你会认真感受连接深度，也在意关系的长期意义。',
		INFP: '你需要真诚、共鸣和不被打扰的情感空间。',
		ENFJ: '你擅长经营氛围，也愿意主动照顾关系温度。',
		ENFP: '你会为心动和可能性投入很多热情。',
		ISTJ: '你更重视可靠、稳定和可以落地的陪伴。',
		ISFJ: '你倾向用体贴和持续投入来维系关系。',
		ESTJ: '你习惯把关系推进得更有秩序和确定感。',
		ESFJ: '你会主动营造安心、温暖、可回应的关系体验。',
		ISTP: '你更偏好轻松、真实、不过度束缚的互动方式。',
		ISFP: '你在关系里很重视感受是否自然舒服。',
		ESTP: '你会被即时互动、行动力和真实体验吸引。',
		ESFP: '你擅长制造轻松快乐的氛围，也重视当下感受。'
	}

	const letterCopy = {
		E: '你通常通过互动确认关系温度，交流本身会给你反馈。',
		I: '你更需要稳定、舒服、低压力的相处节奏，深入比热闹更重要。',
		S: '你会优先看见现实里的可靠、细节和可持续性。',
		N: '你更容易被想法、愿景、潜力和未来感打动。',
		T: '你处理关系问题时会先理清逻辑、边界和解决路径。',
		F: '你会优先判断彼此的感受是否被看见、被接住。',
		J: '你喜欢关系朝更明确、更稳定、更有规划的方向推进。',
		P: '你更希望关系保留弹性，让互动自然生长。'
	}

	const feedbackMap = {
		E: '记录了更主动外放的一面，继续保持直觉作答。',
		I: '记录了更内敛沉静的一面，稳定偏好正在累积。',
		S: '记录了更现实落地的偏好，这会让结果更扎实。',
		N: '记录了更偏未来感和想象力的一面，轮廓更鲜明了。',
		T: '记录了更理性的判断方式，结果正在收束。',
		F: '记录了更感受导向的一面，关系温度线索更清楚了。',
		J: '记录了更偏规划和确定感的倾向，节奏感更稳定了。',
		P: '记录了更偏开放和灵活的倾向，风格开始显现。'
	}

	const userName = ref('')
	const personnelId = ref('')
	const wxOpenid = ref('')
	const helperPageReviewMode = ref(false)
	const currentIndex = ref(0)
	const answers = ref([])
	const questionFlow = ref(buildQuestionFlow())
	const showStageSummary = ref(false)
	const showResult = ref(false)
	const pendingStageNumber = ref(0)
	const selectedDimension = ref('')
	const latestFeedback = ref('')
	const isTransitioning = ref(false)
	const isSavingResult = ref(false)

	const dimensionScores = reactive({
		E: 0,
		I: 0,
		S: 0,
		N: 0,
		T: 0,
		F: 0,
		J: 0,
		P: 0
	})

	onLoad(async (options) => {
		if (options && options.name) {
			userName.value = decodeURIComponent(options.name)
		}
		if (options && options.personnelId) {
			personnelId.value = decodeURIComponent(options.personnelId)
		}
		if (options && options.wxOpenid) {
			wxOpenid.value = decodeURIComponent(options.wxOpenid)
		}
		await loadSystemConfig()
		if (!wxOpenid.value) {
			await resolveWxOpenidFromLogin()
		}
	})

	async function loadSystemConfig() {
		try {
			const result = await personnelUser.getSystemConfig({
				configCode: 'default'
			})
			const config = (result && result.config) || {}
			helperPageReviewMode.value = !!config.helper_page_review_mode
		} catch (error) {
			console.error('loadSystemConfig failed', error)
			helperPageReviewMode.value = false
		}
	}

	function getCandidateOpenIds(user = {}) {
		const loginOpenid = user && user.wx_openid
		if (!loginOpenid) {
			return []
		}
		if (typeof loginOpenid === 'string') {
			const value = loginOpenid.trim()
			return value ? [value] : []
		}
		if (typeof loginOpenid !== 'object') {
			return []
		}
		const preferredKeys = ['mp-weixin', 'mp_weixin', 'mp', 'weixin']
		const values = preferredKeys
			.map((key) => loginOpenid[key])
			.concat(Object.values(loginOpenid || {}))
			.map((item) => (typeof item === 'string' ? item.trim() : ''))
			.filter(Boolean)
		return Array.from(new Set(values))
	}

	async function resolveWxOpenidFromLogin() {
		try {
			const currentUserInfo = getCurrentUserInfo() || {}
			const currentUser = currentUserInfo.userInfo || {}
			const localOpenid = getCandidateOpenIds({
				wx_openid: currentUser.wx_openid || currentUserInfo.wx_openid || ''
			})[0]
			if (localOpenid) {
				wxOpenid.value = localOpenid
				return
			}
			if (!currentUserInfo.uid) {
				return
			}
			const result = await personnelUser.getCurrentLoginWxOpenid({
				uid: currentUserInfo.uid
			})
			wxOpenid.value = (result && result.openIds && result.openIds[0]) || ''
		} catch (error) {
			console.error('resolveWxOpenidFromLogin failed', error)
		}
	}

	const answeredCount = computed(() => answers.value.length)
	const progressPercent = computed(() => Math.round((answeredCount.value / totalQuestions) * 100))
	const currentQuestion = computed(
		() =>
			questionFlow.value[currentIndex.value] || questionFlow.value[questionFlow.value.length - 1]
	)
	const currentStageIndex = computed(() => {
		if (answeredCount.value >= totalQuestions) {
			return stageList.length - 1
		}
		return Math.min(stageList.length - 1, Math.floor(currentIndex.value / stageSize))
	})

	const pageTitle = computed(() => {
		if (showResult.value) {
			return '你的恋爱 MBTI'
		}
		if (showStageSummary.value) {
			return '阶段小结'
		}
		return userName.value ? `${userName.value} 的测试中` : '恋爱 MBTI 测试'
	})

	const pageSubtitle = computed(() => {
		if (showResult.value) {
			return '四个阶段已经全部完成，现在看看你的关系偏好轮廓。'
		}
		if (showStageSummary.value) {
			return '每完成四分之一题量都会生成一次阶段反馈，方便你感受自己的偏好走向。'
		}
		const currentStage = stageList[currentStageIndex.value]
		return `${currentStage.label} · 第 ${(currentIndex.value % stageSize) + 1} / ${stageSize} 题，${currentStage.prompt}`
	})

	const liveHintTitle = computed(() => {
		if (selectedDimension.value) {
			return `已记录：${selectedDimension.value}`
		}
		return `${stageList[currentStageIndex.value].label} · 已完成 ${answeredCount.value} / ${totalQuestions}`
	})

	const liveHintCopy = computed(() => {
		if (selectedDimension.value) {
			return latestFeedback.value
		}
		return stageList[currentStageIndex.value].prompt
	})

	const resultType = computed(() => buildTypeFromCounts(dimensionScores))
	const resultKeywords = computed(() =>
		resultType.value.split('').map((letter) => dimensionKeywords[letter])
	)
	const resultSummary = computed(() => {
		const letters = resultType.value.split('')
		const intro = userName.value ? `${userName.value}，` : ''
		return `${intro}${typeHeadlines[resultType.value]} ${letters.map((letter) => letterCopy[letter]).join(' ')}`
	})

	const resultTraits = computed(() =>
		axisPairs.map((pair) => {
			const leftCount = dimensionScores[pair.left]
			const rightCount = dimensionScores[pair.right]
			const total = leftCount + rightCount || 1
			const dominant = leftCount >= rightCount ? pair.left : pair.right
			const dominantCount = Math.max(leftCount, rightCount)
			return {
				axis: `${pair.left} / ${pair.right}`,
				left: pair.left,
				right: pair.right,
				leftCount,
				rightCount,
				dominant,
				dominantPercent: Math.round((dominantCount / total) * 100),
				fillWidth: Math.max(16, Math.round((dominantCount / total) * 100))
			}
		})
	)

	const stageSummary = computed(() => {
		const stage = stageList[pendingStageNumber.value - 1] || stageList[0]
		const stageAnswers = answers.value.slice(stage.start, stage.end)
		const stageCounts = countDimensions(stageAnswers)
		const stageQuota = Math.max(1, stage.end - stage.start)
		const stageType = buildTypeFromCounts(stageCounts)
		return {
			title: `${stage.label}完成`,
			description: buildStageSummaryDescription({
				stage,
				stageCounts,
				stageType,
				stageAnsweredCount: stageAnswers.length,
				stageQuota
			}),
			personalityDescription: buildStagePersonalityDescription(stageCounts),
			badges: axisPairs.map(
				(pair) =>
					`${pair.label}：${getAxisBadgeText(stageCounts, pair)}（${stageCounts[pair.left]}:${stageCounts[pair.right]}）`
			),
			encouragement: buildStageEncouragement(stage, stageCounts)
		}
	})

	function formatStageIndex(index) {
		return String(index).padStart(2, '0')
	}

	function getStageClass(index) {
		return {
			done: answeredCount.value >= stageList[index].end,
			active:
				index === currentStageIndex.value &&
				!showStageSummary.value &&
				!showResult.value &&
				answeredCount.value < totalQuestions,
			upcoming: answeredCount.value < stageList[index].start
		}
	}

	function countDimensions(list) {
		return list.reduce(
			(acc, item) => {
				acc[item.dimension] += 1
				return acc
			},
			{
				E: 0,
				I: 0,
				S: 0,
				N: 0,
				T: 0,
				F: 0,
				J: 0,
				P: 0
			}
		)
	}

	function shuffleList(list) {
		const cloned = [...list]
		for (let index = cloned.length - 1; index > 0; index -= 1) {
			const randomIndex = Math.floor(Math.random() * (index + 1))
			;[cloned[index], cloned[randomIndex]] = [cloned[randomIndex], cloned[index]]
		}
		return cloned
	}

	function buildQuestionFlow() {
		const flow = []
		const seenQuestionIds = new Set()
		for (let stageIndex = 0; stageIndex < stageList.length; stageIndex += 1) {
			const start = stageIndex * stageSize
			const stageQuestions = questions.slice(start, start + stageSize)
			const shuffledStageQuestions = shuffleList(stageQuestions).filter((question) => {
				if (!question || seenQuestionIds.has(question.id)) {
					return false
				}
				seenQuestionIds.add(question.id)
				return true
			})
			flow.push(...shuffledStageQuestions)
		}

		if (flow.length !== totalQuestions) {
			const remainingQuestions = questions.filter((question) => {
				if (!question || seenQuestionIds.has(question.id)) {
					return false
				}
				seenQuestionIds.add(question.id)
				return true
			})
			flow.push(...remainingQuestions)
		}

		return flow.slice(0, totalQuestions)
	}

	function buildTypeFromCounts(counts) {
		return axisPairs
			.map((pair) => (counts[pair.left] >= counts[pair.right] ? pair.left : pair.right))
			.join('')
	}

	function getAxisBadgeText(counts, pair) {
		return counts[pair.left] >= counts[pair.right] ? pair.badgeLeft : pair.badgeRight
	}

	function getSortedDimensions(counts) {
		return Object.keys(counts)
			.map((key) => ({
				key,
				count: Number(counts[key] || 0)
			}))
			.sort((a, b) => {
				if (b.count !== a.count) {
					return b.count - a.count
				}
				return a.key.localeCompare(b.key)
			})
	}

	function getStrongestAxisTrend(counts) {
		const sorted = axisPairs
			.map((pair) => {
				const leftCount = Number(counts[pair.left] || 0)
				const rightCount = Number(counts[pair.right] || 0)
				const dominant = leftCount >= rightCount ? pair.left : pair.right
				return {
					...pair,
					leftCount,
					rightCount,
					dominant,
					diff: Math.abs(leftCount - rightCount)
				}
			})
			.sort((a, b) => {
				if (b.diff !== a.diff) {
					return b.diff - a.diff
				}
				return a.label.localeCompare(b.label)
			})
		return sorted[0] || null
	}

	function getTrendStrengthWord(diff) {
		if (diff >= 5) {
			return '明显'
		}
		if (diff >= 3) {
			return '比较明显'
		}
		if (diff >= 1) {
			return '轻微'
		}
		return '暂时'
	}

	function buildStageSummaryDescription({
		stage,
		stageCounts,
		stageType,
		stageAnsweredCount,
		stageQuota
	}) {
		const topDimensions = getSortedDimensions(stageCounts).slice(0, 2)
		const topText = topDimensions
			.map((item) => `${item.key}(${item.count})`)
			.join('、')
		const strongestAxis = getStrongestAxisTrend(stageCounts)
		const stageIndex = Math.max(0, pendingStageNumber.value - 1)
		let axisText = ''
		if (strongestAxis) {
			const strengthWord = getTrendStrengthWord(strongestAxis.diff)
			const axisTemplate =
				stageAxisSummaryTemplates[stageIndex] ||
				stageAxisSummaryTemplates[stageAxisSummaryTemplates.length - 1]
			axisText = axisTemplate({
				strongestAxis,
				strengthWord
			})
		}
		const descriptionTemplate =
			stageDescriptionTemplates[stageIndex] ||
			stageDescriptionTemplates[stageDescriptionTemplates.length - 1]
		return descriptionTemplate({
			intro: userName.value ? `${userName.value}，` : '',
			stageAnsweredCount,
			stageQuota,
			stageType,
			topText,
			axisText
		})
	}

	function buildStageEncouragement(stage, stageCounts) {
		const strongestAxis = getStrongestAxisTrend(stageCounts)
		const stageIndex = Math.max(0, pendingStageNumber.value - 1)
		const encouragementTemplate =
			stageEncouragementTemplates[stageIndex] ||
			stageEncouragementTemplates[stageEncouragementTemplates.length - 1]
		if (!strongestAxis || strongestAxis.diff === 0) {
			return encouragementTemplate.balanced(stage)
		}
		return encouragementTemplate.leaning(stage, strongestAxis)
	}

	function buildStagePersonalityDescription(counts) {
		const social = counts.E >= counts.I ? axisPairs[0].sentenceLeft : axisPairs[0].sentenceRight
		const focus = counts.S >= counts.N ? axisPairs[1].sentenceLeft : axisPairs[1].sentenceRight
		const decision = counts.T >= counts.F ? axisPairs[2].sentenceLeft : axisPairs[2].sentenceRight
		const rhythm = counts.J >= counts.P ? axisPairs[3].sentenceLeft : axisPairs[3].sentenceRight
		const stageIndex = Math.max(0, pendingStageNumber.value - 1)
		const personalityTemplate =
			stagePersonalityTemplates[stageIndex] ||
			stagePersonalityTemplates[stagePersonalityTemplates.length - 1]
		return personalityTemplate({
			social,
			focus,
			decision,
			rhythm
		})
	}

	function selectOption(option) {
		if (isTransitioning.value || showStageSummary.value || showResult.value) {
			return
		}

		const question = currentQuestion.value
		answers.value.push({
			questionId: question.id,
			type: question.type,
			dimension: option.dimension,
			text: option.text
		})
		dimensionScores[option.dimension] += 1
		selectedDimension.value = option.dimension
		latestFeedback.value = feedbackMap[option.dimension]
		isTransitioning.value = true

		setTimeout(() => {
			const nextAnsweredCount = answers.value.length
			const nextIndex = currentIndex.value + 1

			if (nextAnsweredCount % stageSize === 0) {
				if (nextAnsweredCount < totalQuestions) {
					currentIndex.value = nextIndex
				}
				pendingStageNumber.value = nextAnsweredCount / stageSize
				showStageSummary.value = true
			} else if (nextAnsweredCount < totalQuestions) {
				currentIndex.value = nextIndex
			}

			selectedDimension.value = ''
			isTransitioning.value = false
		}, 220)
	}

	async function continueToNextStage() {
		showStageSummary.value = false
		if (pendingStageNumber.value === stageList.length && answeredCount.value === totalQuestions) {
			await persistMbtiResult()
			showResult.value = true
			return
		}
		latestFeedback.value = ''
	}

	async function persistMbtiResult() {
		if (helperPageReviewMode.value) {
			return
		}
		if ((!personnelId.value && !wxOpenid.value) || isSavingResult.value) {
			return
		}
		isSavingResult.value = true
		uni.showLoading({
			title: '保存结果中',
			mask: true
		})
		try {
			let targetId = personnelId.value
			if (!targetId && wxOpenid.value) {
				const profileRes = await personnelUser.getByWxOpenid({
					wxOpenid: wxOpenid.value
				})
				targetId = (profileRes && profileRes.record && profileRes.record._id) || ''
			}
			if (!targetId) {
				throw new Error('未找到当前用户档案')
			}
			await personnelUser.saveMbtiResult({
				id: targetId,
				mbti: resultType.value
			})
		} catch (error) {
			uni.showToast({
				title: (error && error.message) || '结果保存失败',
				icon: 'none',
				duration: 3000
			})
		} finally {
			isSavingResult.value = false
			uni.hideLoading()
		}
	}


	function goHome() {
		uni.reLaunch({
			url: '/pages/index/index'
		})
	}
</script>

<style scoped lang="less">
	.page {
		min-height: 100vh;
		background:
			radial-gradient(circle at top left, rgba(255, 194, 159, 0.42), transparent 30%),
			radial-gradient(circle at top right, rgba(135, 202, 255, 0.4), transparent 24%),
			linear-gradient(180deg, #fffdf8 0%, #fff4ec 46%, #fffaf4 100%);
	}

	.hero {
		position: relative;
		min-height: 100vh;
		padding: 56rpx 30rpx 48rpx;
		overflow: hidden;
	}

	.hero-backdrop {
		position: absolute;
		border-radius: 50%;
		filter: blur(10rpx);
		opacity: 0.55;
	}

	.hero-backdrop-left {
		width: 320rpx;
		height: 320rpx;
		left: -120rpx;
		top: -30rpx;
		background: linear-gradient(180deg, #ffd5bc 0%, #ffb58b 100%);
	}

	.hero-backdrop-right {
		width: 280rpx;
		height: 280rpx;
		right: -90rpx;
		top: 220rpx;
		background: linear-gradient(180deg, #cbe8ff 0%, #8ec8ff 100%);
	}

	.hero-copy,
	.progress-card,
	.question-card,
	.summary-card,
	.result-card {
		position: relative;
		z-index: 2;
	}

	.eyebrow,
	.card-eyebrow {
		display: block;
		font-size: 24rpx;
		letter-spacing: 6rpx;
		color: #8d5d41;
	}

	.headline {
		display: block;
		margin-top: 14rpx;
		font-size: 60rpx;
		line-height: 1.18;
		font-weight: 700;
		color: #2f211d;
	}

	.subhead {
		display: block;
		margin-top: 20rpx;
		font-size: 28rpx;
		line-height: 1.7;
		color: #6d5b56;
	}

	.progress-card,
	.question-card,
	.summary-card,
	.result-card {
		margin-top: 30rpx;
		padding: 32rpx 28rpx;
		border-radius: 36rpx;
		background: rgba(255, 255, 255, 0.78);
		box-shadow: 0 20rpx 44rpx rgba(117, 88, 63, 0.1);
		backdrop-filter: blur(10rpx);
	}

	.progress-meta,
	.question-meta,
	.trait-meta {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.progress-title,
	.summary-portrait-label,
	.question-index,
	.trait-axis {
		font-size: 26rpx;
		font-weight: 600;
		color: #49362f;
	}

	.progress-count,
	.question-type,
	.trait-score {
		font-size: 24rpx;
		color: #8a6a5a;
	}

	.progress-track {
		margin-top: 20rpx;
		height: 18rpx;
		border-radius: 999rpx;
		background: rgba(89, 74, 131, 0.12);
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		border-radius: 999rpx;
		background: linear-gradient(90deg, #ffad88 0%, #5c4b85 100%);
		box-shadow: 0 12rpx 22rpx rgba(92, 75, 133, 0.2);
		transition: width 0.28s ease;
	}

	.stage-row {
		display: grid;
		grid-template-columns: repeat(4, minmax(0, 1fr));
		gap: 14rpx;
		margin-top: 24rpx;
	}

	.stage-pill {
		padding: 18rpx 14rpx;
		border-radius: 24rpx;
		background: rgba(255, 255, 255, 0.72);
		border: 2rpx solid rgba(94, 68, 54, 0.08);
	}

	.stage-pill.done {
		background: rgba(91, 75, 133, 0.12);
		border-color: rgba(91, 75, 133, 0.18);
	}

	.stage-pill.active {
		background: linear-gradient(
			135deg,
			rgba(255, 222, 203, 0.92) 0%,
			rgba(234, 228, 255, 0.92) 100%
		);
		border-color: rgba(91, 75, 133, 0.22);
		box-shadow: 0 14rpx 26rpx rgba(91, 75, 133, 0.1);
	}

	.stage-pill.upcoming {
		opacity: 0.76;
	}

	.stage-index {
		display: block;
		font-size: 22rpx;
		letter-spacing: 2rpx;
		color: #8d5d41;
	}

	.stage-label {
		display: block;
		margin-top: 10rpx;
		font-size: 24rpx;
		font-weight: 600;
		color: #3a2a25;
	}

	.summary-title,
	.result-type,
	.question-title {
		display: block;
		margin-top: 16rpx;
		font-size: 40rpx;
		line-height: 1.35;
		font-weight: 700;
		color: #2f211d;
	}

	.summary-copy,
	.result-copy,
	.question-caption,
	.summary-encourage,
	.feedback-copy {
		display: block;
		margin-top: 14rpx;
		font-size: 27rpx;
		line-height: 1.7;
		color: #6d5b56;
	}

	.summary-portrait {
		margin-top: 22rpx;
		padding: 24rpx 22rpx;
		border-radius: 26rpx;
		background: linear-gradient(
			135deg,
			rgba(255, 247, 239, 0.98) 0%,
			rgba(242, 239, 255, 0.98) 100%
		);
	}

	.summary-portrait-copy {
		display: block;
		margin-top: 10rpx;
		font-size: 28rpx;
		line-height: 1.8;
		color: #4e4057;
	}

	.summary-chip-row,
	.result-chip-row {
		display: flex;
		flex-wrap: wrap;
		gap: 14rpx;
		margin-top: 22rpx;
	}

	.summary-chip {
		padding: 14rpx 18rpx;
		border-radius: 999rpx;
		background: rgba(255, 255, 255, 0.92);
		border: 2rpx solid rgba(94, 68, 54, 0.08);
	}

	.summary-chip text {
		font-size: 23rpx;
		color: #594841;
	}

	.accent-chip {
		background: rgba(91, 75, 133, 0.08);
		border-color: rgba(91, 75, 133, 0.12);
	}

	.action-btn {
		min-height: 112rpx;
		padding: 0 24rpx;
		border-radius: 999rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		box-sizing: border-box;
	}

	.action-btn text {
		font-size: 32rpx;
		font-weight: 600;
		line-height: 1;
	}

	.primary-btn {
		margin-top: 28rpx;
		background: linear-gradient(90deg, #2f2a47 0%, #594a83 100%);
		color: #fff9f0;
		box-shadow: 0 18rpx 32rpx rgba(77, 62, 109, 0.22);
	}

	.ghost-btn {
		background: rgba(255, 255, 255, 0.68);
		color: #4e3d37;
		border: 2rpx solid rgba(94, 68, 54, 0.12);
	}

	.option-list {
		margin-top: 26rpx;
	}

	.option-card {
		padding: 28rpx 24rpx;
		border-radius: 28rpx;
		background: rgba(255, 255, 255, 0.94);
		border: 2rpx solid rgba(94, 68, 54, 0.08);
		box-shadow: 0 16rpx 28rpx rgba(117, 88, 63, 0.08);
		transition:
			transform 0.18s ease,
			box-shadow 0.18s ease,
			border-color 0.18s ease;
	}

	.option-card + .option-card {
		margin-top: 18rpx;
	}

	.option-card.selected {
		transform: translateY(-4rpx);
		border-color: rgba(91, 75, 133, 0.28);
		box-shadow: 0 20rpx 34rpx rgba(91, 75, 133, 0.14);
		background: linear-gradient(
			135deg,
			rgba(255, 245, 237, 0.98) 0%,
			rgba(243, 239, 255, 0.98) 100%
		);
	}

	.option-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.option-dimension {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-width: 56rpx;
		height: 56rpx;
		padding: 0 16rpx;
		border-radius: 999rpx;
		background: rgba(91, 75, 133, 0.12);
		font-size: 28rpx;
		font-weight: 700;
		color: #46385a;
	}

	.option-tip {
		font-size: 22rpx;
		color: #9b7f71;
	}

	.option-text {
		display: block;
		margin-top: 18rpx;
		font-size: 31rpx;
		line-height: 1.55;
		color: #342925;
	}

	.feedback-panel {
		margin-top: 24rpx;
		padding: 24rpx 22rpx;
		border-radius: 28rpx;
		background: rgba(255, 248, 241, 0.92);
		border: 2rpx solid rgba(255, 192, 152, 0.2);
	}

	.feedback-title {
		display: block;
		font-size: 26rpx;
		font-weight: 600;
		color: #4a382f;
	}

	.question-card.locked {
		pointer-events: none;
	}

	.trait-list {
		margin-top: 26rpx;
	}

	.trait-item + .trait-item {
		margin-top: 22rpx;
	}

	.trait-track {
		position: relative;
		display: flex;
		margin-top: 12rpx;
		height: 20rpx;
		border-radius: 999rpx;
		overflow: hidden;
		background: rgba(89, 74, 131, 0.08);
	}

	.trait-half {
		flex: 1;
	}

	.trait-left {
		background: rgba(255, 178, 143, 0.34);
	}

	.trait-right {
		background: rgba(139, 200, 255, 0.28);
	}

	.trait-fill {
		position: absolute;
		top: 0;
		bottom: 0;
		border-radius: 999rpx;
		background: linear-gradient(90deg, #ffb28f 0%, #5b4b85 100%);
	}

	.fill-left {
		left: 0;
	}

	.fill-right {
		right: 0;
	}

	.trait-note {
		display: block;
		margin-top: 10rpx;
		font-size: 24rpx;
		color: #7f665b;
	}

	.result-actions {
		display: flex;
		gap: 16rpx;
		margin-top: 28rpx;
	}

	.result-actions .action-btn {
		flex: 1;
		margin-top: 0;
	}

	@media screen and (max-width: 420px) {
		.headline {
			font-size: 54rpx;
		}

		.stage-row {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}

		.result-actions {
			flex-direction: column;
		}
	}
</style>

