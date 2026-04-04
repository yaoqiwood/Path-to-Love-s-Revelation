<template>
	<div class="page">
		<div class="hero">
			<div class="hero-backdrop hero-backdrop-left"></div>
			<div class="hero-backdrop hero-backdrop-right"></div>
			<div class="top-back-btn" @click="goBack">
				<!-- <text class="back-arrow">‹</text> -->
				<text class="back-label">返回</text>
			</div>

			<div class="hero-copy">
				<text class="eyebrow">LOVE MBTI LAB</text>
				<text class="headline">{{ pageTitle }}</text>
				<text class="subhead">{{ pageSubtitle }}</text>
			</div>

			<div class="progress-card">
				<div class="progress-meta">
					<text class="progress-title">答题进度</text>
					<text class="progress-count">{{ answeredCount }}/{{ totalQuestions }}</text>
				</div>
				<div class="progress-track">
					<div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
				</div>
				<div class="stage-row">
					<div
						v-for="(stage, index) in stageList"
						:key="stage.label"
						class="stage-pill"
						:class="getStageClass(index)"
					>
						<text class="stage-index">{{ formatStageIndex(index + 1) }}</text>
						<text class="stage-label">{{ stage.label }}</text>
					</div>
				</div>
			</div>

			<div v-if="showStageSummary" class="summary-card">
				<text class="card-eyebrow">STAGE CHECKPOINT</text>
				<text class="summary-title">{{ stageSummary.title }}</text>
				<text class="summary-copy">{{ stageSummary.description }}</text>

				<div class="summary-portrait">
					<text class="summary-portrait-label">阶段画像</text>
					<text class="summary-portrait-copy">{{ stageSummary.personalityDescription }}</text>
				</div>

				<div class="summary-chip-row">
					<div v-for="item in stageSummary.badges" :key="item" class="summary-chip">
						<text>{{ item }}</text>
					</div>
				</div>

				<text class="summary-encourage">{{ stageSummary.encouragement }}</text>

				<div class="action-btn primary-btn" @click="continueToNextStage">
					<text>{{ pendingStageNumber === stageList.length ? '查看最终结果' : '继续答题' }}</text>
				</div>
			</div>

			<div v-else-if="showResult" class="result-card">
				<text class="card-eyebrow">FINAL RESULT</text>
				<text class="result-type">{{ resultType }}</text>
				<text class="result-copy">{{ resultSummary }}</text>

				<div class="result-chip-row">
					<div v-for="item in resultKeywords" :key="item" class="summary-chip accent-chip">
						<text>{{ item }}</text>
					</div>
				</div>

				<div class="trait-list">
					<div v-for="trait in resultTraits" :key="trait.axis" class="trait-item">
						<div class="trait-meta">
							<text class="trait-axis">{{ trait.axis }}</text>
							<text class="trait-score">{{ trait.leftCount }} : {{ trait.rightCount }}</text>
						</div>
						<div class="trait-track">
							<div class="trait-half trait-left"></div>
							<div class="trait-half trait-right"></div>
							<div
								class="trait-fill"
								:class="trait.dominant === trait.right ? 'fill-right' : 'fill-left'"
								:style="{ width: `${trait.fillWidth}%` }"
							></div>
						</div>
						<text class="trait-note">
							更偏向 {{ trait.dominant }} · {{ trait.dominantPercent }}%
						</text>
					</div>
				</div>

				<div class="result-actions">
					<div class="action-btn ghost-btn" @click="goHome">
						<text>返回首页</text>
					</div>
				</div>
			</div>

			<div v-else class="question-card" :class="{ locked: isTransitioning }">
				<div class="question-meta">
					<text class="question-index">Q{{ currentIndex + 1 }}</text>
					<!-- <text class="question-type">{{ currentQuestion.type }} 维度</text> -->
				</div>

				<text class="question-title">{{ currentQuestion.title }}</text>
				<text class="question-caption">选择更接近你真实状态的一项</text>

				<div class="option-list">
					<div
						v-for="option in currentQuestion.selections"
						:key="`${currentQuestion.id}-${option.dimension}`"
						class="option-card"
						:class="{ selected: selectedDimension === option.dimension }"
						@click="selectOption(option)"
					>
						<div class="option-head">
							<!-- <text class="option-dimension">{{ option.dimension }}</text> -->
							<!-- <text class="option-tip">点击选择</text> -->
						</div>
						<text class="option-text">{{ option.text }}</text>
					</div>
				</div>

				<div class="feedback-panel">
					<text class="feedback-title">{{ liveHintTitle }}</text>
					<text class="feedback-copy">{{ liveHintCopy }}</text>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
	import { computed, nextTick, onMounted, reactive, ref } from 'vue'
	import { useRoute, useRouter } from 'vue-router'
	import questionsSource from '@/data/mbti-88-questions.json'
	import { personnelUserService as personnelUser } from '@/api/modules/personnel-user'
	import { app } from '@/platform/app-bridge'
	import { getCurrentUserInfo } from '@/platform/app-runtime'

	const questions = questionsSource.questions || []
	const totalQuestions = questions.length
	const stageSize = totalQuestions / 4
	const route = useRoute()
	const router = useRouter()

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
			balanced: (stage) =>
				`${stage.encouragement} 这一段还保留着一些摇摆感，继续按直觉选，后面的轮廓会自然拉开。`,
			leaning: (stage, strongestAxis) =>
				`${stage.encouragement} 你在“${strongestAxis.label}”上已经开始偏向一侧，接下来可以看看这种感觉会不会继续加深。`
		},
		{
			balanced: (stage) =>
				`${stage.encouragement} 目前几组维度咬得很紧，这反而说明你的选择很真实，不用刻意放大某一种样子。`,
			leaning: (stage, strongestAxis) =>
				`${stage.encouragement} 到了这里，“${strongestAxis.label}”已经成为比较稳定的一条线索，后面的题目会帮你把它再确认一次。`
		},
		{
			balanced: (stage) =>
				`${stage.encouragement} 现在的你更像是在几个方向之间细细权衡，最后一段往往最能把这种细微差别说清楚。`,
			leaning: (stage, strongestAxis) =>
				`${stage.encouragement} 这一阶段里，“${strongestAxis.label}”的偏好已经不只是偶然冒头了，最后几题会决定它是短暂信号还是核心特征。`
		},
		{
			balanced: (stage) =>
				`${stage.encouragement} 整体来看你不是单一类型的直线答案，而是带着几分平衡感，这会让最终结果更立体。`,
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

	onMounted(async () => {
		const query = route.query || {}
		if (query && query.name) {
			userName.value = decodeURIComponent(String(query.name))
		}
		if (query && query.personnelId) {
			personnelId.value = decodeURIComponent(String(query.personnelId))
		}
		if (query && (query.wxOpenid || query.userId)) {
			wxOpenid.value = decodeURIComponent(String(query.wxOpenid || query.userId))
		}
		await loadSystemConfig()
		if (!wxOpenid.value) {
			await resolveWxOpenidFromLogin()
		}
	})

	async function loadSystemConfig() {
		try {
			const result = await personnelUser.getSystemConfig(
				{
					configCode: 'default'
				},
				{
					skipAuthRedirect: true
				}
			)
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
			if (
				!currentUserInfo.uid ||
				!personnelUser ||
				typeof personnelUser.getCurrentLoginWxOpenid !== 'function'
			) {
				return
			}
			const result = await personnelUser.getCurrentLoginWxOpenid({
				uid: currentUserInfo.uid,
				skipAuthRedirect: true
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
		const topText = topDimensions.map((item) => `${item.key}(${item.count})`).join('、')
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
				void scrollPageToTop()
			} else if (nextAnsweredCount < totalQuestions) {
				currentIndex.value = nextIndex
			}

			selectedDimension.value = ''
			isTransitioning.value = false
		}, 220)
	}

	async function continueToNextStage() {
		if (pendingStageNumber.value === stageList.length && answeredCount.value === totalQuestions) {
			const saved = await persistMbtiResult()
			if (!saved) {
				return
			}
			showStageSummary.value = false
			showResult.value = true
			await scrollPageToTop()
			return
		}
		showStageSummary.value = false
		latestFeedback.value = ''
		await scrollPageToTop()
	}

	async function scrollPageToTop() {
		await nextTick()
		try {
			const scrollOnce = (duration = 0) =>
				new Promise((resolve) => {
					app.pageScrollTo({
						scrollTop: 0,
						duration
					})
					resolve()
				})
			const wait = (delay) =>
				new Promise((resolve) => {
					setTimeout(resolve, delay)
				})
			const resetH5ScrollContainers = () => {
				if (typeof document === 'undefined') {
					return
				}
				const targets = [
					document.scrollingElement,
					document.documentElement,
					document.body,
					document.querySelector('uni-page-body'),
					document.querySelector('.uni-page-body'),
					document.querySelector('.uni-page-wrapper'),
					document.querySelector('.uni-page'),
					document.querySelector('#app'),
					document.querySelector('.page')
				].filter(Boolean)

				targets.forEach((element) => {
					element.scrollTop = 0
				})

				if (typeof window !== 'undefined' && typeof window.scrollTo === 'function') {
					window.scrollTo(0, 0)
				}
			}

			resetH5ScrollContainers()
			await scrollOnce(0)
			await wait(30)
			resetH5ScrollContainers()
			await scrollOnce(180)
			await wait(80)
			resetH5ScrollContainers()
			await scrollOnce(0)
			await wait(120)
			resetH5ScrollContainers()
		} catch (error) {
			console.error('scrollPageToTop failed', error)
		}
	}

	async function persistMbtiResult() {
		if (helperPageReviewMode.value) {
			return true
		}
		if (isSavingResult.value) {
			return false
		}
		isSavingResult.value = true
		app.showLoading({
			title: '保存结果中',
			mask: true
		})
		try {
			await personnelUser.updateMbti(
				{
					mbti: resultType.value
				},
				{
					skipAuthRedirect: true
				}
			)
			return true
		} catch (error) {
			console.error('persistMbtiResult failed', error)
			await app.showModal({
				title: '提示',
				content: '提交失败，请联系相关同工',
				showCancel: false,
				confirmText: '确认'
			})
			return false
		} finally {
			isSavingResult.value = false
			app.hideLoading()
		}
	}

	async function goHome() {
		try {
			await router.push('/pages/index/home')
		} catch (error) {
			console.error('router push to home failed', error)
			app.reLaunch({
				url: '/pages/index/home'
			})
		}
	}

	async function goBack() {
		try {
			await router.back()
		} catch (error) {
			await goHome()
		}
	}
</script>

<style scoped lang="less">
	.page {
		--card-bg: rgba(255, 255, 255, 0.78);
		--card-border: rgba(255, 255, 255, 0.58);
		--text-primary: #2f211d;
		--text-secondary: #6d5b56;
		--text-muted: #8d6f62;
		--accent: #5b4b85;
		--warm: #ffb38a;
		min-height: 100vh;
		background:
			radial-gradient(circle at 10% 12%, rgba(255, 205, 170, 0.48), transparent 24%),
			radial-gradient(circle at 88% 18%, rgba(133, 199, 255, 0.28), transparent 20%),
			linear-gradient(180deg, #fffdf9 0%, #fff5ed 48%, #fffaf5 100%);
	}

	.page,
	.page * {
		box-sizing: border-box;
	}

	.page div,
	.page text {
		display: block;
	}

	.hero {
		position: relative;
		min-height: 100vh;
		max-width: 960px;
		margin: 0 auto;
		padding: calc(42px + var(--safe-top, 0px)) clamp(18px, 4.5vw, 36px)
			calc(48px + var(--safe-bottom, 0px));
		overflow: hidden;
	}

	.hero-backdrop,
	.hero::before {
		position: absolute;
		pointer-events: none;
	}

	.hero::before {
		content: '';
		top: -126px;
		left: 50%;
		width: min(88vw, 720px);
		height: 280px;
		transform: translateX(-50%);
		border-radius: 50%;
		background:
			radial-gradient(circle at center, rgba(255, 255, 255, 0.9), transparent 62%),
			linear-gradient(180deg, rgba(255, 241, 229, 0.62), rgba(255, 255, 255, 0));
	}

	.hero-backdrop {
		border-radius: 999px;
		filter: blur(18px);
		opacity: 0.7;
	}

	.hero-backdrop-left {
		top: 18px;
		left: -96px;
		width: 240px;
		height: 240px;
		background: rgba(255, 187, 141, 0.42);
	}

	.hero-backdrop-right {
		right: -84px;
		top: 190px;
		width: 220px;
		height: 220px;
		background: rgba(142, 200, 255, 0.34);
	}

	.hero-copy,
	.progress-card,
	.question-card,
	.summary-card,
	.result-card {
		position: relative;
		z-index: 1;
	}

	.top-back-btn {
		position: absolute;
		top: calc(16px + var(--safe-top, 0px));
		left: clamp(12px, 2.8vw, 24px);
		z-index: 3;
		min-width: 74px;
		min-height: 36px;
		padding: 0 14px 0 11px;
		border-radius: 999px;
		border: 1px solid rgba(109, 91, 86, 0.16);
		background: rgba(255, 255, 255, 0.92);
		box-shadow: 0 8px 18px rgba(61, 45, 38, 0.12);
		backdrop-filter: blur(4px);
		display: inline-flex;
		align-items: center;
		justify-content: center;
		white-space: nowrap;
		cursor: pointer;
		overflow: hidden;
	}

	.top-back-btn text {
		font-size: 15px;
		font-weight: 600;
		color: #4b3a34;
	}

	.back-arrow {
		position: absolute;
		left: 10px;
		top: 50%;
		transform: translateY(-50%);
		font-size: 18px;
		line-height: 1;
	}

	.back-label {
		position: absolute;
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);
		width: 100%;
		text-align: center;
		padding: 0 16px;
		box-sizing: border-box;
		font-size: 15px;
		font-weight: 700;
		line-height: 1;
	}

	.hero-copy {
		margin-top: 16px;
	}

	.eyebrow,
	.card-eyebrow {
		color: #8f6247;
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.28em;
		text-transform: uppercase;
	}

	.headline {
		margin-top: 14px;
		color: var(--text-primary);
		font-family: var(--font-display);
		font-size: clamp(40px, 7vw, 64px);
		line-height: 1.06;
	}

	.subhead {
		max-width: 34em;
		margin-top: 16px;
		color: var(--text-secondary);
		font-size: 16px;
		line-height: 1.8;
	}

	.progress-card,
	.question-card,
	.summary-card,
	.result-card {
		margin-top: 24px;
		padding: clamp(20px, 4vw, 32px);
		border: 1px solid var(--card-border);
		border-radius: 30px;
		background:
			linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(255, 247, 240, 0.76)), var(--card-bg);
		box-shadow:
			0 24px 48px rgba(117, 88, 63, 0.1),
			inset 0 1px 0 rgba(255, 255, 255, 0.64);
		backdrop-filter: blur(16px);
	}

	.progress-meta,
	.question-meta,
	.trait-meta {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
	}

	.progress-title,
	.summary-portrait-label,
	.question-index,
	.trait-axis,
	.feedback-title {
		color: #4a382f;
		font-size: 15px;
		font-weight: 700;
	}

	.progress-count,
	.trait-score {
		color: var(--text-muted);
		font-size: 14px;
	}

	.progress-track {
		height: 12px;
		margin-top: 18px;
		border-radius: 999px;
		overflow: hidden;
		background: rgba(91, 75, 133, 0.1);
	}

	.progress-fill {
		height: 100%;
		border-radius: inherit;
		background: linear-gradient(90deg, var(--warm) 0%, var(--accent) 100%);
		box-shadow: 0 10px 24px rgba(91, 75, 133, 0.24);
		transition: width 0.28s ease;
	}

	.page .stage-row {
		display: flex;
		align-items: stretch;
		justify-content: space-between;
		gap: 8px;
		margin-top: 20px;
		overflow: hidden;
	}

	.page .stage-row > .stage-pill {
		display: block;
		flex: 1 1 0;
		width: 0;
		min-width: 0;
		padding: 12px 8px;
		border-radius: 18px;
		border: 1px solid rgba(107, 81, 66, 0.08);
		background: rgba(255, 255, 255, 0.72);
		box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
	}

	.stage-pill.done {
		background: rgba(91, 75, 133, 0.1);
		border-color: rgba(91, 75, 133, 0.14);
	}

	.stage-pill.active {
		background: linear-gradient(
			135deg,
			rgba(255, 239, 227, 0.94) 0%,
			rgba(239, 236, 255, 0.94) 100%
		);
		border-color: rgba(91, 75, 133, 0.18);
		box-shadow: 0 12px 24px rgba(91, 75, 133, 0.08);
	}

	.stage-pill.upcoming {
		opacity: 0.72;
	}

	.stage-index {
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 0.18em;
		color: #9c7258;
	}

	.stage-label {
		margin-top: 8px;
		color: #372924;
		font-size: 14px;
		line-height: 1.45;
		font-weight: 700;
	}

	.summary-title,
	.result-type,
	.question-title {
		margin-top: 14px;
		color: var(--text-primary);
		font-size: clamp(28px, 4.8vw, 42px);
		line-height: 1.18;
		font-weight: 700;
	}

	.summary-copy,
	.result-copy,
	.question-caption,
	.summary-encourage,
	.feedback-copy,
	.summary-portrait-copy,
	.trait-note {
		margin-top: 14px;
		color: var(--text-secondary);
		font-size: 15px;
		line-height: 1.8;
	}

	.question-caption {
		color: var(--text-muted);
	}

	.summary-portrait,
	.feedback-panel {
		margin-top: 22px;
		padding: 18px 18px 20px;
		border-radius: 24px;
	}

	.summary-portrait {
		background: linear-gradient(
			135deg,
			rgba(255, 248, 241, 0.98) 0%,
			rgba(241, 239, 255, 0.98) 100%
		);
	}

	.feedback-panel {
		border: 1px solid rgba(255, 191, 150, 0.22);
		background: linear-gradient(180deg, rgba(255, 248, 241, 0.95), rgba(255, 243, 232, 0.9));
	}

	.summary-chip-row,
	.result-chip-row {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		margin-top: 20px;
	}

	.summary-chip {
		padding: 10px 14px;
		border-radius: 999px;
		border: 1px solid rgba(107, 81, 66, 0.08);
		background: rgba(255, 255, 255, 0.9);
	}

	.summary-chip text {
		color: #594841;
		font-size: 13px;
		line-height: 1.35;
	}

	.accent-chip {
		background: rgba(91, 75, 133, 0.08);
		border-color: rgba(91, 75, 133, 0.12);
	}

	.action-btn {
		width: 100%;
		min-height: 56px;
		padding: 0 24px;
		border-radius: 999px;
		box-sizing: border-box;
	}

	.action-btn text {
		font-size: 16px;
		font-weight: 700;
		line-height: 56px;
		text-align: center;
	}

	.primary-btn {
		margin-top: 26px;
		background: linear-gradient(90deg, #2f2a47 0%, #594a83 100%);
		color: #fff9f0;
		box-shadow: 0 18px 32px rgba(77, 62, 109, 0.22);
	}

	.ghost-btn {
		background: rgba(255, 255, 255, 0.72);
		color: #4e3d37;
		border: 1px solid rgba(94, 68, 54, 0.12);
	}

	.option-list {
		display: grid;
		gap: 16px;
		margin-top: 24px;
	}

	.option-card {
		padding: 20px;
		border-radius: 24px;
		background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(255, 249, 244, 0.92));
		border: 1px solid rgba(94, 68, 54, 0.08);
		box-shadow: 0 18px 30px rgba(117, 88, 63, 0.08);
		transition:
			transform 0.18s ease,
			box-shadow 0.18s ease,
			border-color 0.18s ease;
	}

	.option-card + .option-card {
		margin-top: 0;
	}

	.option-card.selected {
		transform: translateY(-2px);
		border-color: rgba(91, 75, 133, 0.28);
		box-shadow: 0 24px 38px rgba(91, 75, 133, 0.14);
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
		gap: 12px;
	}

	.option-tip {
		font-size: 12px;
		font-weight: 600;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: #9b7f71;
	}

	.option-text {
		margin-top: 14px;
		font-size: 18px;
		line-height: 1.6;
		color: #342925;
	}

	.question-card.locked {
		pointer-events: none;
	}

	.trait-list {
		display: grid;
		gap: 18px;
		margin-top: 24px;
	}

	.trait-item + .trait-item {
		margin-top: 0;
	}

	.trait-track {
		position: relative;
		display: flex;
		margin-top: 12px;
		height: 14px;
		border-radius: 999px;
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
		border-radius: inherit;
		background: linear-gradient(90deg, #ffb28f 0%, #5b4b85 100%);
	}

	.fill-left {
		left: 0;
	}

	.fill-right {
		right: 0;
	}

	.result-actions {
		display: flex;
		gap: 14px;
		margin-top: 26px;
	}

	.result-actions .action-btn {
		flex: 1;
		margin-top: 0;
	}

	@media screen and (max-width: 760px) {
		.option-text {
			font-size: 16px;
		}
	}

	@media screen and (max-width: 520px) {
		.hero {
			padding-left: 16px;
			padding-right: 16px;
		}

		.progress-card,
		.question-card,
		.summary-card,
		.result-card {
			padding: 18px;
			border-radius: 26px;
		}

		.result-actions {
			flex-direction: column;
		}
	}
</style>
