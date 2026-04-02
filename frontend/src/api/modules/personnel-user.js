import { http, unwrapResponse } from '@/api/http'
import { withMockFallback } from '@/api/mockService'
import { apiUrls } from '@/api/urls'
import { getAuthStorageValue, AUTH_STORAGE_KEYS } from '@/platform/auth-storage'

const STORAGE_KEYS = {
	personnel: 'mock-db-personnel',
	heartMessages: 'mock-db-heart-messages',
	systemConfig: 'mock-db-system-config',
	priorityBoards: 'mock-db-priority-boards'
}

const DEFAULT_SYSTEM_CONFIG = {
	helper_page_review_mode: true,
	enable_heart_chat_page: true
}

const PERSONA_ASSET_MAP = {
	INFP: '/static/mbti-personas/infp.svg',
	ENFP: '/static/mbti-personas/enfp.svg',
	INFJ: '/static/mbti-personas/infj.svg',
	ENFJ: '/static/mbti-personas/enfj.svg',
	INTP: '/static/mbti-personas/intp.svg',
	ENTP: '/static/mbti-personas/entp.svg',
	ISFP: '/static/mbti-personas/isfp.svg',
	ESFP: '/static/mbti-personas/esfp.svg',
	ISTJ: '/static/mbti-personas/istj.svg',
	ESTJ: '/static/mbti-personas/estj.svg',
	INTJ: '/static/mbti-personas/intj.svg',
	ESFJ: '/static/mbti-personas/esfj.svg'
}

const PRIORITY_BOARD_LIMIT = 10

const PRIORITY_CANDIDATE_NAME_MAP = {
	female: [
		['Lina Hart', 'Lina'],
		['Mira Snow', 'Mira'],
		['Nora Reed', 'Nora'],
		['Ivy Lane', 'Ivy'],
		['June Vale', 'June'],
		['Ella Bloom', 'Ella'],
		['Ruby Shore', 'Ruby'],
		['Clara West', 'Clara'],
		['Tessa Quinn', 'Tessa'],
		['Vera Moss', 'Vera'],
		['Naomi Wells', 'Naomi'],
		['Sophie Ray', 'Sophie'],
		['Ariel Ford', 'Ariel'],
		['Celia Moon', 'Celia'],
		['Mabel Stone', 'Mabel'],
		['Daisy Hunt', 'Daisy'],
		['Hazel Brooks', 'Hazel'],
		['Iris Cole', 'Iris'],
		['Leah Hart', 'Leah'],
		['Nina Drew', 'Nina'],
		['Olive Page', 'Olive'],
		['Piper Scott', 'Piper'],
		['Stella Finch', 'Stella'],
		['Wendy Frost', 'Wendy']
	],
	male: [
		['Evan Reed', 'Evan'],
		['Noah Grant', 'Noah'],
		['Luca Stone', 'Luca'],
		['Owen Hart', 'Owen'],
		['Miles Quinn', 'Miles'],
		['Eli Ford', 'Eli'],
		['Logan West', 'Logan'],
		['Ian Brooks', 'Ian'],
		['Aiden Cole', 'Aiden'],
		['Caleb Frost', 'Caleb'],
		['Julian Page', 'Julian'],
		['Theo Scott', 'Theo'],
		['Ryan Vale', 'Ryan'],
		['Mason Drew', 'Mason'],
		['Leo Hunt', 'Leo'],
		['Asher Lane', 'Asher'],
		['Nolan Wells', 'Nolan'],
		['Carter Moss', 'Carter'],
		['Felix Ray', 'Felix'],
		['Ethan Moon', 'Ethan'],
		['Silas Bloom', 'Silas'],
		['Roman Shore', 'Roman'],
		['Levi Snow', 'Levi'],
		['Jonah Finch', 'Jonah']
	]
}

const PRIORITY_CANDIDATE_STYLE_MAP = {
	female: {
		mbtis: [
			'INFP',
			'INFJ',
			'INTJ',
			'ISFP',
			'ENFP',
			'ESFJ',
			'INTP',
			'ENFJ',
			'INFP',
			'ISTJ',
			'ESFP',
			'ENTP'
		],
		cities: [
			'Shanghai',
			'Suzhou',
			'Wuhan',
			'Fuzhou',
			'Beijing',
			'Hefei',
			'Hangzhou',
			'Nanjing',
			'Xiamen',
			'Chengdu',
			'Qingdao',
			'Ningbo'
		],
		professions: [
			'Brand Planner',
			'Counseling Assistant',
			'Algorithm Engineer',
			'Illustrator',
			'Product Manager',
			'Teacher',
			'Spatial Designer',
			'Documentary Editor',
			'Music Therapist',
			'Nonprofit Coordinator',
			'Copywriter',
			'Student Advisor'
		],
		churches: [
			'City Church',
			'Grace Spring Church',
			'Youth Fellowship',
			'Morning Light Fellowship',
			'Walk Together Fellowship',
			'New Town Fellowship',
			'Brookside Church',
			'Hope Fellowship',
			'Coastline Church',
			'Good Friends Group',
			'Olive Branch Fellowship',
			'True Way Church'
		],
		intros: [
			'She values steady replies and likes to know someone in a calm, consistent rhythm.',
			'She can turn an ordinary dinner into a meaningful conversation and is honest about feelings.',
			'She does not rush a relationship but remembers small details people casually mention.',
			'She likes warmth with boundaries, and comfort matters more than pure excitement.',
			'She hopes two people can grow together while still leaving each other room to breathe.',
			'She is drawn to clarity, sincerity, and reliability rather than hot-and-cold signals.'
		],
		tagSets: [
			['slow burn', 'good listener', 'responds well'],
			['clear boundary', 'steady', 'not flaky'],
			['gentle', 'detail aware', 'patient'],
			['honest', 'communicative', 'relational'],
			['easygoing', 'empathetic', 'low drama'],
			['long-term', 'thoughtful', 'sustainable']
		]
	},
	male: {
		mbtis: [
			'ENFP',
			'ENTP',
			'ESFP',
			'ESTJ',
			'ENFJ',
			'ISTJ',
			'INTJ',
			'INFP',
			'ENTP',
			'ESFJ',
			'ENFP',
			'INTP'
		],
		cities: [
			'Hangzhou',
			'Chengdu',
			'Xiamen',
			'Ningbo',
			'Nanjing',
			'Qingdao',
			'Shanghai',
			'Suzhou',
			'Beijing',
			'Wuhan',
			'Shenzhen',
			'Chongqing'
		],
		professions: [
			'Event Curator',
			'Photographer',
			'Sports Therapist',
			'Operations Lead',
			'Youth Ministry Coordinator',
			'Project Manager',
			'Architectural Designer',
			'Podcast Producer',
			'Startup Partner',
			'Product Operations',
			'Brand Director',
			'Music Teacher'
		],
		churches: [
			'Grace Fellowship',
			'Living Water Church',
			'Coastline Church',
			'Harbor Church',
			'Gospel Hall',
			'North Shore Fellowship',
			'Morning Light Fellowship',
			'Wilderness Group',
			'Valley Church',
			'Grace Friends Fellowship',
			'Green Field Fellowship',
			'Spring Source Church'
		],
		intros: [
			'He likes creating easygoing chemistry and can also step up when a relationship needs direction.',
			'He enjoys novelty, but what really holds his attention is steadiness and truthfulness.',
			'He is willing to show interest clearly and back it up with action.',
			'He is not into flashy routines and trusts slow-built reliability more than big gestures.',
			'He is drawn to substantial conversations and wants both warmth and direction.',
			'He appreciates honesty, clarity, and responsive communication over ambiguity.'
		],
		tagSets: [
			['expressive', 'keeps convo going', 'high energy'],
			['reliable', 'shows up', 'acts on words'],
			['communicative', 'has boundaries', 'not performative'],
			['steady pace', 'follows through', 'patient'],
			['warm', 'attentive', 'good atmosphere'],
			['direct', 'long-term', 'responsible']
		]
	}
}
function clone(value) {
	return JSON.parse(JSON.stringify(value))
}

function safeReadStorage(key, fallback) {
	const rawValue = localStorage.getItem(key)
	if (!rawValue) {
		return clone(fallback)
	}

	try {
		return JSON.parse(rawValue)
	} catch (error) {
		console.warn(`Failed to parse storage key ${key}.`, error)
		return clone(fallback)
	}
}

function safeWriteStorage(key, value) {
	localStorage.setItem(key, JSON.stringify(value))
}

function nowText() {
	return new Date().toISOString()
}

function normalizeText(value) {
	return String(value || '').trim()
}

function normalizeUpper(value) {
	return normalizeText(value).toUpperCase()
}

function normalizeKeyword(value) {
	return normalizeText(value).toLowerCase()
}

function toNumber(value) {
	const result = Number(value)
	return Number.isFinite(result) ? result : 0
}

function normalizeGender(value) {
	const text = normalizeLower(value)
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

function buildSeedPersonnel() {
	return [
		{
			_id: 'personnel-101',
			person_id: 101,
			name: '林知夏',
			nickname: '知夏',
			gender: '女',
			age: 25,
			mobile: '1380000101',
			mbti: 'INFP',
			native_place: '上海',
			profession: '品牌策划',
			church: '城市教会',
			referrer: '周牧师',
			self_introduction: '喜欢写字、散步和慢慢认识一个人。',
			relationship_status: '单身',
			travel_mode: '地铁',
			address: '上海市徐汇区',
			family_overview: '父母在外地生活，独立居住。',
			review_status: 'approved',
			reviewer: '管理员',
			passcode: 'LOVE101',
			user_role: 0,
			personal_photo: PERSONA_ASSET_MAP.INFP,
			user_id: '',
			private_message_quota: 2,
			heart_message_quota: 3,
			remaining_heart_value: 3,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-102',
			person_id: 102,
			name: '周以安',
			nickname: '以安',
			gender: '男',
			age: 27,
			mobile: '1380000102',
			mbti: 'ENFP',
			native_place: '杭州',
			profession: '活动策展',
			church: '恩典团契',
			referrer: '李长老',
			self_introduction: '爱热闹，也会认真照顾每一个人的情绪。',
			relationship_status: '单身',
			travel_mode: '自驾',
			address: '杭州市滨江区',
			family_overview: '和父母关系亲密，周末会回家吃饭。',
			review_status: 'approved',
			reviewer: '管理员',
			passcode: 'LOVE102',
			user_role: 2,
			personal_photo: PERSONA_ASSET_MAP.ENFP,
			user_id: 'mock-user-102',
			private_message_quota: 4,
			heart_message_quota: 5,
			remaining_heart_value: 5,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-103',
			person_id: 103,
			name: '沈未央',
			nickname: '未央',
			gender: '女',
			age: 26,
			mobile: '1380000103',
			mbti: 'INFJ',
			native_place: '苏州',
			profession: '心理咨询助理',
			church: '恩泉教会',
			referrer: '陈同工',
			self_introduction: '重视真诚回应，也很珍惜被理解的时刻。',
			relationship_status: '单身',
			travel_mode: '地铁',
			address: '苏州市工业园区',
			family_overview: '家庭氛围温和，比较看重彼此支持。',
			review_status: 'approved',
			reviewer: '管理员',
			passcode: 'LOVE103',
			user_role: 1,
			personal_photo: PERSONA_ASSET_MAP.INFJ,
			user_id: 'mock-user-103',
			private_message_quota: 3,
			heart_message_quota: 4,
			remaining_heart_value: 4,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-104',
			person_id: 104,
			name: '顾星野',
			nickname: '星野',
			gender: '男',
			age: 28,
			mobile: '1380000104',
			mbti: 'ENFJ',
			native_place: '南京',
			profession: '青年事工协调',
			church: '福音堂',
			referrer: '赵传道',
			self_introduction: '喜欢把复杂事情安排得明白，也喜欢把人照顾好。',
			relationship_status: '单身',
			travel_mode: '地铁',
			address: '南京市鼓楼区',
			family_overview: '常和家人一起服事。',
			review_status: 'approved',
			reviewer: '管理员',
			passcode: 'LOVE104',
			user_role: 3,
			personal_photo: PERSONA_ASSET_MAP.ENFJ,
			user_id: 'mock-user-104',
			private_message_quota: 6,
			heart_message_quota: 6,
			remaining_heart_value: 6,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-105',
			person_id: 105,
			name: '许清岚',
			nickname: '清岚',
			gender: '女',
			age: 24,
			mobile: '1380000105',
			mbti: 'INTP',
			native_place: '武汉',
			profession: '算法工程师',
			church: '青苗团契',
			referrer: '团契同工',
			self_introduction: '聊天慢热，但会认真记住对方说过的话。',
			relationship_status: '单身',
			travel_mode: '公交',
			address: '武汉市洪山区',
			family_overview: '家里重视教育，关系稳定。',
			review_status: 'pending',
			reviewer: '',
			passcode: 'LOVE105',
			user_role: 0,
			personal_photo: PERSONA_ASSET_MAP.INTP,
			user_id: '',
			private_message_quota: 2,
			heart_message_quota: 3,
			remaining_heart_value: 3,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-106',
			person_id: 106,
			name: '程景和',
			nickname: '景和',
			gender: '男',
			age: 29,
			mobile: '1380000106',
			mbti: 'ENTP',
			native_place: '成都',
			profession: '自由摄影师',
			church: '活水教会',
			referrer: '诗班朋友',
			self_introduction: '喜欢新鲜想法，也愿意用行动制造惊喜。',
			relationship_status: '单身',
			travel_mode: '自驾',
			address: '成都市高新区',
			family_overview: '家中排行老大。',
			review_status: 'approved',
			reviewer: '管理员',
			passcode: 'LOVE106',
			user_role: 2,
			personal_photo: PERSONA_ASSET_MAP.ENTP,
			user_id: 'mock-user-106',
			private_message_quota: 5,
			heart_message_quota: 4,
			remaining_heart_value: 4,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-107',
			person_id: 107,
			name: '顾南枝',
			nickname: '南枝',
			gender: '女',
			age: 26,
			mobile: '1380000107',
			mbti: 'ISFP',
			native_place: '福州',
			profession: '插画师',
			church: '晨光团契',
			referrer: '周姐妹',
			self_introduction: '更习惯用细节表达好感。',
			relationship_status: '单身',
			travel_mode: '公交',
			address: '福州市鼓楼区',
			family_overview: '家里关系亲密，喜欢一起旅行。',
			review_status: 'approved',
			reviewer: '管理员',
			passcode: 'LOVE107',
			user_role: 0,
			personal_photo: PERSONA_ASSET_MAP.ISFP,
			user_id: '',
			private_message_quota: 1,
			heart_message_quota: 2,
			remaining_heart_value: 2,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-108',
			person_id: 108,
			name: '陆晨风',
			nickname: '晨风',
			gender: '男',
			age: 24,
			mobile: '1380000108',
			mbti: 'ESFP',
			native_place: '厦门',
			profession: '运动康复师',
			church: '海风教会',
			referrer: '王同工',
			self_introduction: '开心的时候会想第一时间分享给喜欢的人。',
			relationship_status: '单身',
			travel_mode: '电动车',
			address: '厦门市思明区',
			family_overview: '和弟弟感情很好。',
			review_status: 'approved',
			reviewer: '管理员',
			passcode: 'LOVE108',
			user_role: 0,
			personal_photo: PERSONA_ASSET_MAP.ESFP,
			user_id: '',
			private_message_quota: 2,
			heart_message_quota: 3,
			remaining_heart_value: 3,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-109',
			person_id: 109,
			name: '宋知白',
			nickname: '知白',
			gender: '男',
			age: 30,
			mobile: '1380000109',
			mbti: 'ISTJ',
			native_place: '青岛',
			profession: '项目经理',
			church: '北岸团契',
			referrer: '刘长老',
			self_introduction: '稳定和兑现承诺，比华丽表达更重要。',
			relationship_status: '单身',
			travel_mode: '自驾',
			address: '青岛市市南区',
			family_overview: '家庭观念强，愿意承担责任。',
			review_status: 'rejected',
			reviewer: '管理员',
			passcode: 'LOVE109',
			user_role: 0,
			personal_photo: PERSONA_ASSET_MAP.ISTJ,
			user_id: '',
			private_message_quota: 0,
			heart_message_quota: 2,
			remaining_heart_value: 2,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-110',
			person_id: 110,
			name: '徐沐阳',
			nickname: '沐阳',
			gender: '男',
			age: 27,
			mobile: '1380000110',
			mbti: 'ESTJ',
			native_place: '宁波',
			profession: '门店运营',
			church: '港湾教会',
			referrer: '同工推荐',
			self_introduction: '喜欢明确关系方向，也习惯主动推进。',
			relationship_status: '单身',
			travel_mode: '地铁',
			address: '宁波市鄞州区',
			family_overview: '家庭成员关系稳定。',
			review_status: 'approved',
			reviewer: '管理员',
			passcode: 'LOVE110',
			user_role: 1,
			personal_photo: PERSONA_ASSET_MAP.ESTJ,
			user_id: 'mock-user-110',
			private_message_quota: 3,
			heart_message_quota: 3,
			remaining_heart_value: 3,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-111',
			person_id: 111,
			name: '白屿',
			nickname: '白屿',
			gender: '女',
			age: 25,
			mobile: '1380000111',
			mbti: 'INTJ',
			native_place: '北京',
			profession: '产品经理',
			church: '同行团契',
			referrer: '校友',
			self_introduction: '认真时会很投入，也会为关系做长期计划。',
			relationship_status: '单身',
			travel_mode: '打车',
			address: '北京市朝阳区',
			family_overview: '父母支持自己在外发展。',
			review_status: 'approved',
			reviewer: '管理员',
			passcode: 'LOVE111',
			user_role: 0,
			personal_photo: PERSONA_ASSET_MAP.INTJ,
			user_id: '',
			private_message_quota: 1,
			heart_message_quota: 2,
			remaining_heart_value: 2,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-112',
			person_id: 112,
			name: '江晚棠',
			nickname: '晚棠',
			gender: '女',
			age: 23,
			mobile: '1380000112',
			mbti: 'ESFJ',
			native_place: '合肥',
			profession: '教师',
			church: '新城团契',
			referrer: '青年小组',
			self_introduction: '会认真经营关系，也很在意回应感。',
			relationship_status: '单身',
			travel_mode: '公交',
			address: '合肥市蜀山区',
			family_overview: '习惯照顾家里人的情绪。',
			review_status: 'approved',
			reviewer: '管理员',
			passcode: 'LOVE112',
			user_role: 0,
			personal_photo: PERSONA_ASSET_MAP.ESFJ,
			user_id: '',
			private_message_quota: 2,
			heart_message_quota: 3,
			remaining_heart_value: 3,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		},
		{
			_id: 'personnel-113',
			person_id: 113,
			name: '管理员',
			nickname: '管理员',
			gender: '男',
			age: 30,
			mobile: '1380000113',
			mbti: 'INTJ',
			native_place: '上海',
			profession: '系统管理员',
			church: '城市教会',
			referrer: '系统',
			self_introduction: '系统管理员，负责平台的日常维护和管理。',
			relationship_status: '单身',
			travel_mode: '自驾',
			address: '上海市浦东新区',
			family_overview: '家庭关系和睦。',
			review_status: 'approved',
			reviewer: '系统',
			passcode: 'LOVE113',
			user_role: 3,
			personal_photo: PERSONA_ASSET_MAP.INTJ,
			user_id: 'mock-user-113',
			private_message_quota: 6,
			heart_message_quota: 6,
			remaining_heart_value: 6,
			submitted_at: nowText(),
			updated_at: nowText(),
			is_deleted: false
		}
	]
}

function buildSeedHeartMessages() {
	return [
		{
			_id: 'heart-1',
			sender_record_id: 'personnel-102',
			receiver_record_id: 'personnel-101',
			content: '如果你愿意，我们可以从一顿饭开始慢慢认识。',
			status: 'delivered',
			is_anonymous: false,
			quota_cost: 1,
			user_remark: '首次问候',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
			created_at_text: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString()
		},
		{
			_id: 'heart-2',
			sender_record_id: 'personnel-101',
			receiver_record_id: 'personnel-102',
			content: '可以呀，我也想听听你最近在忙什么。',
			status: 'delivered',
			is_anonymous: false,
			quota_cost: 1,
			user_remark: '',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 10).toISOString(),
			created_at_text: new Date(Date.now() - 1000 * 60 * 60 * 10).toISOString()
		},
		{
			_id: 'heart-3',
			sender_record_id: 'personnel-103',
			receiver_record_id: 'personnel-101',
			content: '你的自我介绍给人一种很安静的力量。',
			status: 'delivered',
			is_anonymous: true,
			quota_cost: 1,
			user_remark: '匿名来信',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
			created_at_text: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString()
		},
		{
			_id: 'heart-4',
			sender_record_id: 'personnel-101',
			receiver_record_id: 'personnel-103',
			content: '谢谢你，我也很喜欢你文字里的温柔。',
			status: 'delivered',
			is_anonymous: false,
			quota_cost: 1,
			user_remark: '',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
			created_at_text: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString()
		},
		{
			_id: 'heart-5',
			sender_record_id: 'personnel-106',
			receiver_record_id: 'personnel-101',
			content: '今晚有空的话，一起去看夜景吗？',
			status: 'queued',
			is_anonymous: false,
			quota_cost: 1,
			user_remark: '',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
			created_at_text: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString()
		}
	]
}

function getPersonnelList() {
	const cachedList = safeReadStorage(STORAGE_KEYS.personnel, [])
	if (Array.isArray(cachedList) && cachedList.length) {
		return cachedList
	}

	const seedList = buildSeedPersonnel()
	safeWriteStorage(STORAGE_KEYS.personnel, seedList)
	return seedList
}

function savePersonnelList(list) {
	safeWriteStorage(STORAGE_KEYS.personnel, list)
}
function ensureInboxMockSeedMessages(list = []) {
	const sourceList = Array.isArray(list) ? list : []
	const nextList = [...sourceList]
	const existingIds = new Set(sourceList.map((item) => normalizeText(item && item._id)))

	const seedSpecs = [
		{
			_id: 'heart-inbox-seed-31',
			senderId: 'personnel-111',
			receiverId: 'personnel-102',
			content: 'Anonymous inbox: your boundaries feel warm and clear.',
			hoursAgo: 1.4,
			isAnonymous: true,
			userRemark: 'inbox-anonymous'
		},
		{
			_id: 'heart-inbox-seed-32',
			senderId: 'personnel-106',
			receiverId: 'personnel-103',
			content: 'Anonymous inbox: your listening style feels very safe.',
			hoursAgo: 1.2,
			isAnonymous: true,
			userRemark: 'inbox-anonymous'
		},
		{
			_id: 'heart-inbox-seed-33',
			senderId: 'personnel-102',
			receiverId: 'personnel-108',
			content: 'Anonymous inbox: your social vibe is really comfortable.',
			hoursAgo: 1.0,
			isAnonymous: true,
			userRemark: 'inbox-anonymous'
		},
		{
			_id: 'heart-inbox-seed-34',
			senderId: 'personnel-104',
			receiverId: 'personnel-107',
			content: 'Anonymous inbox: your sincerity makes me want to know you more.',
			hoursAgo: 0.9,
			isAnonymous: true,
			userRemark: 'inbox-anonymous'
		},
		{
			_id: 'heart-inbox-seed-35',
			senderId: 'personnel-103',
			receiverId: 'personnel-110',
			content: 'Anonymous inbox: you are quiet but strong in a good way.',
			hoursAgo: 0.8,
			isAnonymous: true,
			userRemark: 'inbox-anonymous'
		},
		{
			_id: 'heart-inbox-seed-36',
			senderId: 'personnel-107',
			receiverId: 'personnel-101',
			content: 'Anonymous inbox: your view on relationship pace resonates with me.',
			hoursAgo: 0.7,
			isAnonymous: true,
			userRemark: 'inbox-anonymous'
		},
		{
			_id: 'heart-inbox-seed-37',
			senderId: 'personnel-101',
			receiverId: 'personnel-107',
			content: 'Thanks for your inbox letter. I would like to continue chatting.',
			hoursAgo: 0.5,
			isAnonymous: false,
			userRemark: 'inbox-reply'
		},
		{
			_id: 'heart-inbox-seed-38',
			senderId: 'personnel-112',
			receiverId: 'personnel-106',
			content: 'Anonymous inbox: your replies feel sincere and grounded.',
			hoursAgo: 0.4,
			isAnonymous: true,
			userRemark: 'inbox-anonymous'
		}
	]

	let changed = false

	for (let index = 0; index < seedSpecs.length; index += 1) {
		const spec = seedSpecs[index]
		const id = normalizeText(spec._id)
		if (!id || existingIds.has(id)) {
			continue
		}

		const sender = getPersonnelById(spec.senderId)
		const receiver = getPersonnelById(spec.receiverId)
		if (!sender || !receiver) {
			continue
		}

		const timestamp = new Date(Date.now() - toNumber(spec.hoursAgo) * 60 * 60 * 1000).toISOString()
		nextList.push({
			_id: id,
			sender_record_id: sender._id,
			receiver_record_id: receiver._id,
			content: normalizeText(spec.content),
			status: 'delivered',
			is_anonymous: !!spec.isAnonymous,
			quota_cost: 1,
			user_remark: normalizeText(spec.userRemark),
			message_scene: 'inbox',
			created_at: timestamp,
			created_at_text: timestamp
		})

		existingIds.add(id)
		changed = true
	}

	return {
		list: nextList,
		changed
	}
}

function getHeartMessageList() {
	const cachedList = safeReadStorage(STORAGE_KEYS.heartMessages, [])
	if (Array.isArray(cachedList) && cachedList.length) {
		const patchedCached = ensureInboxMockSeedMessages(cachedList)
		if (patchedCached.changed) {
			safeWriteStorage(STORAGE_KEYS.heartMessages, patchedCached.list)
		}
		return patchedCached.list
	}

	const seedList = buildSeedHeartMessages()
	const patchedSeedList = ensureInboxMockSeedMessages(seedList)
	safeWriteStorage(STORAGE_KEYS.heartMessages, patchedSeedList.list)
	return patchedSeedList.list
}

function saveHeartMessageList(list) {
	safeWriteStorage(STORAGE_KEYS.heartMessages, list)
}

function getPriorityBoardList() {
	return safeReadStorage(STORAGE_KEYS.priorityBoards, [])
}

function savePriorityBoardList(list) {
	safeWriteStorage(STORAGE_KEYS.priorityBoards, list)
}

function buildPriorityBoardStorageId(personnelId) {
	return `priority-board-${normalizeText(personnelId) || 'anonymous'}`
}

function getOppositeGender(gender) {
	if (gender === 'female') {
		return 'male'
	}
	if (gender === 'male') {
		return 'female'
	}
	return ''
}

function buildPriorityCandidateRecord(entry, index, gender) {
	const candidateStyleMap =
		PRIORITY_CANDIDATE_STYLE_MAP[gender] || PRIORITY_CANDIDATE_STYLE_MAP.female
	const [name, nickname] = Array.isArray(entry) ? entry : ['', '']
	const styleIndex = index % candidateStyleMap.mbtis.length
	const mbti = candidateStyleMap.mbtis[styleIndex] || 'INFP'
	const ageBase = gender === 'female' ? 23 : 24
	const tags = candidateStyleMap.tagSets[index % candidateStyleMap.tagSets.length] || []

	return {
		_id: `priority-${gender}-${String(index + 1).padStart(2, '0')}`,
		name: normalizeText(name),
		nickname: normalizeText(nickname),
		gender,
		age: ageBase + (index % 6),
		mbti,
		city: candidateStyleMap.cities[styleIndex] || '',
		profession: candidateStyleMap.professions[styleIndex] || '',
		church: candidateStyleMap.churches[styleIndex] || '',
		intro: candidateStyleMap.intros[index % candidateStyleMap.intros.length] || '',
		tags: tags.map((item) => normalizeText(item)).filter(Boolean),
		personal_photo: PERSONA_ASSET_MAP[mbti] || ''
	}
}

function isPriorityBoardCandidateForUser(candidate, selfRecord = {}) {
	const candidateId = normalizeText(candidate && candidate._id)
	const selfId = normalizeText(selfRecord && selfRecord._id)
	if (!candidateId || candidateId === selfId) {
		return false
	}

	if (toNumber(candidate && candidate.user_role) !== 0) {
		return false
	}

	const selfGender = normalizeGender(selfRecord && selfRecord.gender)
	const candidateGender = normalizeGender(candidate && candidate.gender)
	if (!selfGender || !candidateGender) {
		return true
	}

	return selfGender !== candidateGender
}

function getPriorityCandidateList(selfRecord = {}) {
	return getActivePersonnel()
		.filter((item) => isPriorityBoardCandidateForUser(item, selfRecord))
		.map((item) => ({
			...item,
			_id: normalizeText(item._id)
		}))
}

function getPriorityBoardTargetGender(selfRecord = {}) {
	return getOppositeGender(normalizeGender(selfRecord && selfRecord.gender)) || ''
}

function normalizePriorityBoardCandidateGender(candidateGender = '') {
	return candidateGender === 'male' || candidateGender === 'female' ? candidateGender : ''
}

function normalizePriorityBoardIds(ids, selfRecord = {}) {
	const candidateIdSet = new Set(
		getPriorityCandidateList(selfRecord).map((item) => normalizeText(item._id))
	)
	const seenIdSet = new Set()

	return (Array.isArray(ids) ? ids : [])
		.map((item) => normalizeText(item))
		.filter((item) => {
			if (!item || seenIdSet.has(item) || !candidateIdSet.has(item)) {
				return false
			}
			seenIdSet.add(item)
			return true
		})
		.slice(0, PRIORITY_BOARD_LIMIT)
}

function normalizePriorityBoardStatus(status, selectedCount) {
	return normalizeText(status) === 'submitted' && selectedCount === PRIORITY_BOARD_LIMIT
		? 'submitted'
		: 'draft'
}

function createDefaultPriorityBoardRecord(personnelId, candidateGender) {
	const normalizedCandidateGender = normalizePriorityBoardCandidateGender(candidateGender)
	return {
		_id: buildPriorityBoardStorageId(personnelId),
		personnel_id: normalizeText(personnelId),
		candidate_gender: normalizedCandidateGender,
		status: 'draft',
		selected_ids: [],
		created_at: nowText(),
		updated_at: nowText(),
		submitted_at: ''
	}
}

function getPriorityBoardRecord(personnelId, selfRecord = {}) {
	const normalizedPersonnelId = normalizeText(personnelId)
	const normalizedCandidateGender = normalizePriorityBoardCandidateGender(
		getPriorityBoardTargetGender(selfRecord)
	)
	const boardList = getPriorityBoardList()
	const currentIndex = boardList.findIndex(
		(item) => normalizeText(item && item.personnel_id) === normalizedPersonnelId
	)

	if (currentIndex < 0) {
		return createDefaultPriorityBoardRecord(normalizedPersonnelId, normalizedCandidateGender)
	}

	const existingRecord = boardList[currentIndex] || {}
	const normalizedIds = normalizePriorityBoardIds(existingRecord.selected_ids, selfRecord)
	const normalizedStatus = normalizePriorityBoardStatus(existingRecord.status, normalizedIds.length)
	const nextRecord = {
		...createDefaultPriorityBoardRecord(normalizedPersonnelId, normalizedCandidateGender),
		...existingRecord,
		personnel_id: normalizedPersonnelId,
		candidate_gender: normalizedCandidateGender,
		selected_ids: normalizedIds,
		status: normalizedStatus
	}

	if (
		normalizeText(existingRecord.candidate_gender) !== normalizedCandidateGender ||
		JSON.stringify(existingRecord.selected_ids || []) !== JSON.stringify(normalizedIds) ||
		normalizeText(existingRecord.status) !== normalizedStatus
	) {
		boardList.splice(currentIndex, 1, {
			...nextRecord,
			updated_at: nowText(),
			submitted_at: normalizedStatus === 'submitted' ? existingRecord.submitted_at || nowText() : ''
		})
		savePriorityBoardList(boardList)
		return boardList[currentIndex]
	}

	return nextRecord
}

function upsertPriorityBoardRecord(personnelId, patch = {}, selfRecord = {}) {
	const normalizedPersonnelId = normalizeText(personnelId)
	const normalizedCandidateGender = normalizePriorityBoardCandidateGender(
		getPriorityBoardTargetGender(selfRecord)
	)
	const boardList = getPriorityBoardList()
	const currentIndex = boardList.findIndex(
		(item) => normalizeText(item && item.personnel_id) === normalizedPersonnelId
	)
	const baseRecord =
		currentIndex >= 0
			? getPriorityBoardRecord(normalizedPersonnelId, selfRecord)
			: createDefaultPriorityBoardRecord(normalizedPersonnelId, normalizedCandidateGender)
	const nextSelectedIds = normalizePriorityBoardIds(
		typeof patch.selected_ids === 'undefined' ? baseRecord.selected_ids : patch.selected_ids,
		selfRecord
	)
	const nextStatus = normalizePriorityBoardStatus(
		typeof patch.status === 'undefined' ? baseRecord.status : patch.status,
		nextSelectedIds.length
	)
	const nextRecord = {
		...baseRecord,
		...patch,
		personnel_id: normalizedPersonnelId,
		candidate_gender: normalizedCandidateGender,
		selected_ids: nextSelectedIds,
		status: nextStatus,
		updated_at: nowText(),
		submitted_at:
			nextStatus === 'submitted'
				? normalizeText(patch.submitted_at || baseRecord.submitted_at || nowText())
				: ''
	}

	if (currentIndex >= 0) {
		boardList.splice(currentIndex, 1, nextRecord)
	} else {
		boardList.unshift(nextRecord)
	}

	savePriorityBoardList(boardList)
	return nextRecord
}

function buildPriorityBoardResponse(personnelId) {
	const { personnelId: normalizedPersonnelId, selfRecord } =
		resolveCurrentPersonnelRecord(personnelId)
	if (!selfRecord) {
		const emptyBoard = createDefaultPriorityBoardRecord(normalizedPersonnelId, 'female')
		return {
			self: null,
			board: {
				...emptyBoard,
				limit: PRIORITY_BOARD_LIMIT,
				selected_count: 0,
				available_slots: PRIORITY_BOARD_LIMIT
			},
			candidates: [],
			selected: [],
			summary: {
				targetGender: 'female',
				totalCandidates: 0,
				selectedCount: 0,
				progressPercent: 0
			}
		}
	}

	const targetGender = getPriorityBoardTargetGender(selfRecord)
	const candidates = getPriorityCandidateList(selfRecord)
	const candidateMap = candidates.reduce((accumulator, item) => {
		accumulator[item._id] = item
		return accumulator
	}, {})
	const boardRecord = getPriorityBoardRecord(normalizedPersonnelId, selfRecord)
	const selected = boardRecord.selected_ids
		.map((item) => candidateMap[normalizeText(item)])
		.filter(Boolean)

	return {
		self: {
			...selfRecord,
			priority_target_gender: targetGender
		},
		board: {
			...boardRecord,
			limit: PRIORITY_BOARD_LIMIT,
			selected_count: selected.length,
			available_slots: Math.max(0, PRIORITY_BOARD_LIMIT - selected.length)
		},
		candidates,
		selected,
		summary: {
			targetGender,
			totalCandidates: candidates.length,
			selectedCount: selected.length,
			progressPercent: Math.round((selected.length / PRIORITY_BOARD_LIMIT) * 100)
		}
	}
}

function savePriorityBoardDraft(personnelId, orderedIds) {
	const { personnelId: normalizedPersonnelId, selfRecord } =
		resolveCurrentPersonnelRecord(personnelId)
	if (!selfRecord) {
		throw new Error('未找到当前用户档案')
	}

	upsertPriorityBoardRecord(
		normalizedPersonnelId,
		{
			selected_ids: orderedIds,
			status: 'draft',
			submitted_at: ''
		},
		selfRecord
	)

	return buildPriorityBoardResponse(normalizedPersonnelId)
}

function submitPriorityBoard(personnelId, orderedIds) {
	const { personnelId: normalizedPersonnelId, selfRecord } =
		resolveCurrentPersonnelRecord(personnelId)
	if (!selfRecord) {
		throw new Error('未找到当前用户档案')
	}

	const normalizedIds = normalizePriorityBoardIds(orderedIds, selfRecord)
	if (normalizedIds.length !== PRIORITY_BOARD_LIMIT) {
		throw new Error('请先选满 10 位心动对象并完成排序')
	}

	upsertPriorityBoardRecord(
		normalizedPersonnelId,
		{
			selected_ids: normalizedIds,
			status: 'submitted',
			submitted_at: nowText()
		},
		selfRecord
	)

	return buildPriorityBoardResponse(normalizedPersonnelId)
}

function getSystemConfigValue() {
	const config = safeReadStorage(STORAGE_KEYS.systemConfig, DEFAULT_SYSTEM_CONFIG)
	if (!config || typeof config !== 'object') {
		return clone(DEFAULT_SYSTEM_CONFIG)
	}
	return {
		...DEFAULT_SYSTEM_CONFIG,
		...config
	}
}

function getActivePersonnel(includeDeleted = false) {
	const fullList = getPersonnelList()
	return fullList.filter((item) => (includeDeleted ? true : !item.is_deleted))
}

function getPersonnelById(id) {
	return getPersonnelList().find((item) => item._id === normalizeText(id)) || null
}

function resolveCurrentPersonnelId(fallbackPersonnelId = '') {
	const profile = getAuthStorageValue(AUTH_STORAGE_KEYS.profile)
	const profileId = normalizeText(profile && (profile.personnel_id || profile._id || profile.id))
	if (profileId) {
		return profileId
	}

	const session = getAuthStorageValue(AUTH_STORAGE_KEYS.session)
	const sessionUserId = normalizeText(
		(session &&
			(session.uid || (session.userInfo && (session.userInfo._id || session.userInfo.id)))) ||
			''
	)
	if (sessionUserId) {
		const byUserId = getPersonnelList().find(
			(item) => normalizeText(item && item.user_id) === sessionUserId
		)
		if (byUserId && byUserId._id) {
			return normalizeText(byUserId._id)
		}
	}

	return normalizeText(fallbackPersonnelId)
}

function resolveCurrentPersonnelRecord(fallbackPersonnelId = '') {
	const resolvedPersonnelId = resolveCurrentPersonnelId(fallbackPersonnelId)
	return {
		personnelId: resolvedPersonnelId,
		selfRecord: getPersonnelById(resolvedPersonnelId)
	}
}

function updatePersonnelRecord(id, patch) {
	const nextList = getPersonnelList().map((item) => {
		if (item._id !== id) {
			return item
		}

		return {
			...item,
			...patch,
			updated_at: nowText()
		}
	})

	savePersonnelList(nextList)
	return getPersonnelById(id)
}

function buildLoginProfileRecord(record = {}) {
	return {
		_id: record._id || '',
		person_id: toNumber(record.person_id),
		nickname: normalizeText(record.nickname),
		name: normalizeText(record.name),
		passcode: normalizeText(record.passcode),
		review_status: normalizeText(record.review_status) || 'pending',
		user_role: toNumber(record.user_role),
		personal_photo: normalizeText(record.personal_photo),
		user_id: normalizeText(record.user_id),
		submitted_at: record.submitted_at || '',
		updated_at: record.updated_at || ''
	}
}

function findPersonnelByPasscode(passcode = '') {
	const normalizedPasscode = normalizeUpper(passcode)
	if (!normalizedPasscode) {
		return null
	}

	return (
		getActivePersonnel().find((item) => normalizeUpper(item.passcode) === normalizedPasscode) ||
		null
	)
}

function filterPersonnel(list, keyword) {
	const normalizedKeyword = normalizeKeyword(keyword)
	if (!normalizedKeyword) {
		return list
	}

	return list.filter((item) =>
		[item.person_id, item.nickname, item.name, item.mobile, item.mbti, item.passcode]
			.map((value) => normalizeKeyword(value))
			.some((value) => value.includes(normalizedKeyword))
	)
}

function buildPersonnelStats(list) {
	return {
		total: list.length,
		pending: list.filter((item) => item.review_status === 'pending').length,
		approved: list.filter((item) => item.review_status === 'approved').length,
		rejected: list.filter((item) => item.review_status === 'rejected').length
	}
}

function paginateList(list, page = 1, pageSize = 10) {
	const currentPage = Math.max(1, toNumber(page) || 1)
	const normalizedPageSize = Math.max(1, toNumber(pageSize) || 10)
	const start = (currentPage - 1) * normalizedPageSize
	return {
		list: list.slice(start, start + normalizedPageSize),
		page: currentPage,
		pageSize: normalizedPageSize,
		total: list.length
	}
}

function ensureUniqueId(prefix) {
	return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function nextPersonId() {
	return (
		getPersonnelList().reduce(
			(maxValue, item) => Math.max(maxValue, toNumber(item.person_id)),
			100
		) + 1
	)
}

function buildCanSendState(personnelId, contactId) {
	const conversation = getConversation(personnelId, contactId)
	const latestMessage = conversation[conversation.length - 1]
	if (!latestMessage) {
		return {
			can_send: true,
			can_send_reason: ''
		}
	}

	if (latestMessage.sender_record_id === personnelId) {
		return {
			can_send: false,
			can_send_reason: '请等待对方回复后再发送下一条'
		}
	}

	return {
		can_send: true,
		can_send_reason: ''
	}
}

function getConversation(personnelId, contactId) {
	return getHeartMessageList()
		.filter((item) => {
			const members = [item.sender_record_id, item.receiver_record_id]
			return members.includes(personnelId) && members.includes(contactId)
		})
		.sort(
			(left, right) => new Date(left.created_at).getTime() - new Date(right.created_at).getTime()
		)
}

function buildContactSummary(targetRecord, selfRecord, allMessages) {
	const conversation = allMessages
		.filter((item) => {
			const members = [item.sender_record_id, item.receiver_record_id]
			return members.includes(selfRecord._id) && members.includes(targetRecord._id)
		})
		.sort(
			(left, right) => new Date(left.created_at).getTime() - new Date(right.created_at).getTime()
		)

	const latestMessage = conversation[conversation.length - 1] || null
	const canSend = !latestMessage || latestMessage.sender_record_id !== selfRecord._id

	return {
		_id: targetRecord._id,
		name: targetRecord.name,
		nickname: targetRecord.nickname,
		gender: targetRecord.gender,
		mbti: targetRecord.mbti,
		personal_photo: targetRecord.personal_photo || '',
		latest_message: latestMessage?.content || '',
		latest_message_at: latestMessage?.created_at || '',
		can_send: canSend
	}
}

function listContactsForUser(personnelId, keyword) {
	const selfRecord = getPersonnelById(personnelId)
	if (!selfRecord) {
		return {
			self: null,
			contacts: []
		}
	}

	const allPersonnel = getActivePersonnel()
	const allMessages = getHeartMessageList()
	const contacts = allPersonnel
		.filter((item) => item._id !== selfRecord._id)
		.map((item) => buildContactSummary(item, selfRecord, allMessages))
		.filter(
			(item) =>
				filterPersonnel(
					[
						{
							...item,
							person_id: getPersonnelById(item._id)?.person_id || ''
						}
					],
					keyword
				).length > 0
		)
		.sort((left, right) => {
			const leftTime = new Date(left.latest_message_at || 0).getTime()
			const rightTime = new Date(right.latest_message_at || 0).getTime()
			return rightTime - leftTime
		})

	return {
		self: selfRecord,
		contacts
	}
}

function buildInboxList(personnelId, keyword) {
	const selfRecord = getPersonnelById(personnelId)
	if (!selfRecord) {
		return {
			self: null,
			list: []
		}
	}

	const contacts = listContactsForUser(personnelId, keyword).contacts
	const list = contacts
		.filter((item) => {
			const conversation = getConversation(personnelId, item._id)
			const latestMessage = conversation[conversation.length - 1]
			return latestMessage && latestMessage.sender_record_id !== personnelId
		})
		.map((item) => {
			const conversation = getConversation(personnelId, item._id)
			const latestMessage = conversation[conversation.length - 1]
			return {
				message_id: latestMessage?._id || '',
				contact_id: item._id,
				sender_mbti: item.mbti || '-',
				content: latestMessage?.content || '',
				created_at: latestMessage?.created_at || ''
			}
		})

	return {
		self: selfRecord,
		list
	}
}

function getConversationVersion(personnelId) {
	const conversation = getHeartMessageList().filter(
		(item) => item.sender_record_id === personnelId || item.receiver_record_id === personnelId
	)
	return conversation.length
		? `${conversation.length}-${conversation[conversation.length - 1].created_at}`
		: '0-empty'
}

function getInboxVersion(personnelId) {
	const inboxList = buildInboxList(personnelId).list
	return inboxList.length ? `${inboxList.length}-${inboxList[0].created_at}` : '0-empty'
}

function buildHeartbeatState(personnelId) {
	return {
		contactsVersion: getConversationVersion(personnelId),
		inboxVersion: getInboxVersion(personnelId)
	}
}

function buildHeartMessageAdminStats(list) {
	return {
		total: list.length,
		queued: list.filter((item) => item.status === 'queued').length,
		delivered: list.filter((item) => item.status === 'delivered').length,
		draft: list.filter((item) => item.status === 'draft').length,
		revoked: list.filter((item) => item.status === 'revoked').length
	}
}

function enrichHeartMessage(item) {
	const sender = getPersonnelById(item.sender_record_id) || {}
	const receiver = getPersonnelById(item.receiver_record_id) || {}
	return {
		...item,
		sender_person_id: sender.person_id || '',
		sender_name: sender.name || '',
		sender_nickname: sender.nickname || '',
		sender_mbti: sender.mbti || '',
		receiver_person_id: receiver.person_id || '',
		receiver_name: receiver.name || '',
		receiver_nickname: receiver.nickname || '',
		receiver_mbti: receiver.mbti || ''
	}
}

function buildIntentRankingList() {
	const personnel = getActivePersonnel()
	const pairSeed = [
		[personnel[0], personnel[1], 9, 7, 'submitted', 'submitted'],
		[personnel[2], personnel[3], 8, 8, 'locked', 'locked'],
		[personnel[4], personnel[5], 6, 5, 'submitted', 'draft'],
		[personnel[6], personnel[7], 4, 7, 'draft', 'submitted'],
		[personnel[8], personnel[11], 10, 9, 'locked', 'submitted']
	]

	return pairSeed
		.filter((item) => item[0] && item[1])
		.map((item, index) => {
			const [left, right, leftRank, rightRank, leftStatus, rightStatus] = item
			const scoreLeft = Math.max(0, 11 - leftRank) * 10
			const scoreRight = Math.max(0, 11 - rightRank) * 10
			const mutualBonusScore = Math.min(scoreLeft, scoreRight) * 1.2
			const pairStatus =
				leftStatus === 'locked' || rightStatus === 'locked'
					? 'locked'
					: leftStatus === 'submitted' && rightStatus === 'submitted'
						? 'submitted'
						: 'draft'

			return {
				pair_key: `${left._id}__${right._id}`,
				pair_rank: index + 1,
				match_score_total: Math.round(scoreLeft + scoreRight + mutualBonusScore),
				pair_status: pairStatus,
				rank_left_to_right: leftRank,
				rank_right_to_left: rightRank,
				score_left_to_right: scoreLeft,
				score_right_to_left: scoreRight,
				mutual_bonus_score: mutualBonusScore,
				left_status: leftStatus,
				right_status: rightStatus,
				left_submitted_at: left.updated_at,
				left_updated_at: left.updated_at,
				right_submitted_at: right.updated_at,
				right_updated_at: right.updated_at,
				left_person: {
					person_id: left.person_id,
					name: left.name,
					nickname: left.nickname,
					mbti: left.mbti
				},
				right_person: {
					person_id: right.person_id,
					name: right.name,
					nickname: right.nickname,
					mbti: right.mbti
				}
			}
		})
}

function buildWeightedRankingList() {
	return buildIntentRankingList()
		.map((item) => ({
			...item,
			match_score_total:
				(item.rank_left_to_right > 10 ? 1000 : item.rank_left_to_right) +
				(item.rank_right_to_left > 10 ? 1000 : item.rank_right_to_left)
		}))
		.sort((left, right) => left.match_score_total - right.match_score_total)
		.map((item, index) => ({
			...item,
			pair_rank: index + 1
		}))
}

function buildIntentStats(list) {
	const scoreList = list.map((item) => toNumber(item.match_score_total))
	return {
		totalPairs: list.length,
		filteredPairs: list.length,
		totalMatchScore: scoreList.reduce((sum, value) => sum + value, 0),
		topMatchScore: scoreList.length ? Math.max(...scoreList) : 0,
		lowestMatchScore: scoreList.length ? Math.min(...scoreList) : 0
	}
}

function getLocalUserHeartPriorityBoard({ personnelId } = {}) {
	return buildPriorityBoardResponse(normalizeText(personnelId))
}

function saveLocalUserHeartPriorityBoard({ personnelId, orderedIds = [] } = {}) {
	return savePriorityBoardDraft(normalizeText(personnelId), orderedIds)
}

function submitLocalUserHeartPriorityBoard({ personnelId, orderedIds = [] } = {}) {
	return submitPriorityBoard(normalizeText(personnelId), orderedIds)
}

export {
	getPersonnelList,
	getHeartMessageList,
	getSystemConfigValue,
	getPersonnelById,
	updatePersonnelRecord,
	getLocalUserHeartPriorityBoard,
	saveLocalUserHeartPriorityBoard,
	submitLocalUserHeartPriorityBoard
}
export const personnelUserService = {
	async getSystemConfig(params = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.personnel.systemConfig(), {
						params
					})
				),
			async () => ({
				config: getSystemConfigValue()
			})
		)
	},

	async listLoginProfiles({ keyword = '', reviewStatus = 'all', limit = 20 } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.personnel.loginProfiles(), {
						params: {
							keyword,
							reviewStatus,
							limit
						}
					})
				),
			async () => {
				const maxLimit = Math.max(1, toNumber(limit) || 20)
				const list = filterPersonnel(getActivePersonnel(), keyword)
					.filter((item) => (reviewStatus === 'all' ? true : item.review_status === reviewStatus))
					.slice(0, maxLimit)
					.map((item) => buildLoginProfileRecord(item))

				return { list }
			}
		)
	},

	async getLoginProfileByPasscode({ passcode = '' } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.personnel.loginProfile(), {
						params: {
							passcode
						}
					})
				),
			async () => {
				const record = findPersonnelByPasscode(passcode)
				return {
					matched: !!record,
					record: record ? buildLoginProfileRecord(record) : null
				}
			}
		)
	},

	async loginByPasscode({
		passcode = '',
		personnelId = '',
		personId = 0,
		name = '',
		nickname = ''
	} = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.post(apiUrls.personnel.login(), {
						passcode
					})
				),
			async () => {
				const record = findPersonnelByPasscode(passcode)
				if (!record) {
					throw new Error('未找到对应口令，请检查后重新输入。')
				}

				if (normalizeText(personnelId) && normalizeText(personnelId) !== normalizeText(record._id)) {
					throw new Error('人员身份确认失败，请重新匹配。')
				}

				if (toNumber(personId) && toNumber(personId) !== toNumber(record.person_id)) {
					throw new Error('人员编号校验失败，请重新匹配。')
				}

				if (normalizeText(name) && normalizeText(name) !== normalizeText(record.name)) {
					throw new Error('姓名校验失败，请重新匹配。')
				}

				if (normalizeText(nickname) && normalizeText(nickname) !== normalizeText(record.nickname)) {
					throw new Error('昵称校验失败，请重新匹配。')
				}

				if (normalizeText(record.review_status) !== 'approved') {
					throw new Error('当前人员档案未通过审核')
				}

				return {
					access_token: `mock-token-${record.user_id || record._id || 'guest'}`,
					token_type: 'bearer',
					profile: buildLoginProfileRecord(record)
				}
			}
		)
	},

	async searchNames({ keyword = '', limit = 5 } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.personnel.searchNames(), {
						params: {
							keyword,
							limit
						}
					})
				),
			async () => {
				const list = filterPersonnel(getActivePersonnel(), keyword)
					.filter((item) => normalizeText(item.name))
					.slice(0, Math.max(1, toNumber(limit) || 5))
					.map((item) => ({
						_id: item._id,
						name: item.name,
						user_role: item.user_role
					}))
				return { list }
			}
		)
	},

	async list({
		keyword = '',
		reviewStatus = 'all',
		page = 1,
		pageSize = 8,
		includeDeleted = false
	} = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.personnel.list(), {
						params: {
							keyword,
							reviewStatus,
							page,
							pageSize,
							includeDeleted
						}
					})
				),
			async () => {
				const sourceList = getActivePersonnel(includeDeleted)
				const filteredList = filterPersonnel(
					sourceList.filter((item) => {
						if (reviewStatus === 'all') {
							return true
						}
						return item.review_status === reviewStatus
					}),
					keyword
				).sort((left, right) => toNumber(right.person_id) - toNumber(left.person_id))

				const pageData = paginateList(filteredList, page, pageSize)

				return {
					...pageData,
					stats: buildPersonnelStats(getActivePersonnel())
				}
			}
		)
	},

	async create({ data } = {}) {
		return withMockFallback(
			async () => unwrapResponse(await http.post(apiUrls.personnel.create(), data)),
			async () => {
				const generatedPersonId = nextPersonId()
				const nextRecord = {
					_id: ensureUniqueId('personnel'),
					person_id: generatedPersonId,
					review_status: 'pending',
					reviewer: '',
					passcode: `LOVE${generatedPersonId}`,
					user_role: 0,
					personal_photo: '',
					user_id: '',
					private_message_quota: 0,
					heart_message_quota: 3,
					remaining_heart_value: 3,
					submitted_at: nowText(),
					updated_at: nowText(),
					is_deleted: false,
					...data
				}

				const list = getPersonnelList()
				list.unshift(nextRecord)
				savePersonnelList(list)

				return {
					id: nextRecord._id,
					person_id: nextRecord.person_id
				}
			}
		)
	},

	async update({ id, data } = {}) {
		return withMockFallback(
			async () => unwrapResponse(await http.put(apiUrls.personnel.byId(id), data)),
			async () => {
				const nextRecord = updatePersonnelRecord(normalizeText(id), data || {})
				return {
					...(nextRecord || {}),
					id: nextRecord?._id || normalizeText(id)
				}
			}
		)
	},

	async softDelete({ id } = {}) {
		return withMockFallback(
			async () => unwrapResponse(await http.delete(apiUrls.personnel.byId(id))),
			async () => {
				updatePersonnelRecord(normalizeText(id), {
					is_deleted: true
				})
				return {
					id: normalizeText(id)
				}
			}
		)
	},

	async resetAllPasscodes() {
		return withMockFallback(
			async () => unwrapResponse(await http.post(apiUrls.personnel.resetAllPasscodes())),
			async () => {
				const nextList = getPersonnelList().map((item) => ({
					...item,
					passcode: `LOVE${item.person_id}`,
					updated_at: nowText()
				}))
				savePersonnelList(nextList)
				return {
					updatedCount: nextList.length
				}
			}
		)
	},

	async importExcel() {
		return withMockFallback(
			async (...args) => unwrapResponse(await http.post(apiUrls.personnel.importExcel(), ...args)),
			async () => {
				const createdRecords = [
					{
						nickname: '新月',
						name: '梁新月',
						gender: '女',
						age: 24,
						mobile: '1380000201',
						mbti: 'INFP'
					},
					{
						nickname: '牧川',
						name: '顾牧川',
						gender: '男',
						age: 27,
						mobile: '1380000202',
						mbti: 'ENFJ'
					}
				]

				for (const record of createdRecords) {
					await this.create({
						data: record
					})
				}

				return {
					importedCount: createdRecords.length,
					skippedCount: 0,
					errors: []
				}
			}
		)
	},

	async upsertByUser({ userId, data } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(await http.post(apiUrls.personnel.upsertByUser(), { userId, data })),
			async () => {
				const normalizedUserId = normalizeText(userId)
				const normalizedPasscode = normalizeUpper(data?.passcode)
				const list = getPersonnelList()
				let target =
					list.find((item) => normalizeText(item.user_id) === normalizedUserId) ||
					list.find((item) => normalizeUpper(item.passcode) === normalizedPasscode)

				if (!target) {
					return {
						ok: false,
						matched: false,
						updated: false,
						skipped: true,
						message: '邀请码填写错误，请联系相关人员'
					}
				}

				target = updatePersonnelRecord(target._id, {
					...data,
					user_id: normalizedUserId,
					passcode: target.passcode || normalizedPasscode
				})

				return {
					id: target._id,
					person_id: target.person_id,
					name: target.name,
					passcode: target.passcode,
					user_role: target.user_role,
					mbti: target.mbti,
					personal_photo: target.personal_photo
				}
			}
		)
	},

	async saveMbtiResult({ id, mbti } = {}) {
		return withMockFallback(
			async () => unwrapResponse(await http.post(apiUrls.personnel.saveMbtiResult(id), { mbti })),
			async () => {
				updatePersonnelRecord(normalizeText(id), {
					mbti: normalizeUpper(mbti)
				})
				return {
					id: normalizeText(id),
					mbti: normalizeUpper(mbti)
				}
			}
		)
	},

	async listUsers({ keyword = '' } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.personnel.users(), {
						params: {
							keyword
						}
					})
				),
			async () => {
				const list = filterPersonnel(
					getActivePersonnel().filter(
						(item) => toNumber(item.user_role) === 2 || toNumber(item.user_role) === 3
					),
					keyword
				)
				return {
					list,
					stats: {
						total: list.length,
						users: list.filter((item) => toNumber(item.user_role) === 2).length,
						superUsers: list.filter((item) => toNumber(item.user_role) === 3).length
					}
				}
			}
		)
	},

	async listUserCandidates({ keyword = '' } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.personnel.userCandidates(), {
						params: {
							keyword
						}
					})
				),
			async () => ({
				list: filterPersonnel(
					getActivePersonnel().filter((item) => toNumber(item.user_role) === 0),
					keyword
				)
			})
		)
	},

	async updateUserRole({ id, userRole } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(await http.patch(apiUrls.personnel.updateUserRole(id), { userRole })),
			async () => {
				const nextRecord = updatePersonnelRecord(normalizeText(id), {
					user_role: toNumber(userRole)
				})
				return {
					id: nextRecord?._id || normalizeText(id),
					user_role: nextRecord?.user_role || 0
				}
			}
		)
	},

	async listPrivateMessageCandidates({ keyword = '' } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.heartMessages.candidates(), {
						params: {
							keyword
						}
					})
				),
			async () => ({
				list: filterPersonnel(getActivePersonnel(), keyword).map((item) => ({
					...item,
					label: `#${item.person_id} · ${item.nickname || '-'} / ${item.name || '-'}`
				}))
			})
		)
	},

	async updatePrivateMessageQuota({ id, value, mode } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.patch(apiUrls.personnel.updatePrivateMessageQuota(id), {
						value,
						mode
					})
				),
			async () => {
				const currentRecord = getPersonnelById(normalizeText(id))
				const currentQuota = toNumber(currentRecord?.private_message_quota)
				const delta = Math.max(0, toNumber(value))
				let nextQuota = currentQuota

				if (mode === 'set') {
					nextQuota = delta
				} else if (mode === 'increase') {
					nextQuota += delta
				} else if (mode === 'decrease') {
					nextQuota = Math.max(0, currentQuota - delta)
				}

				const nextRecord = updatePersonnelRecord(normalizeText(id), {
					private_message_quota: nextQuota
				})

				return {
					id: nextRecord?._id || normalizeText(id),
					private_message_quota: nextQuota
				}
			}
		)
	},

	async listHeartMessages({ keyword = '', status = 'all' } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.heartMessages.list(), {
						params: {
							keyword,
							status
						}
					})
				),
			async () => {
				const list = getHeartMessageList()
					.map((item) => enrichHeartMessage(item))
					.filter((item) => {
						if (status === 'all') {
							return true
						}
						return item.status === status
					})
					.filter((item) =>
						normalizeKeyword(JSON.stringify(item)).includes(normalizeKeyword(keyword))
					)

				return {
					list,
					stats: buildHeartMessageAdminStats(list)
				}
			}
		)
	},

	async createHeartMessage({ data } = {}) {
		return withMockFallback(
			async () => unwrapResponse(await http.post(apiUrls.heartMessages.create(), data)),
			async () => {
				const nextRecord = {
					_id: ensureUniqueId('heart'),
					status: 'queued',
					quota_cost: 1,
					is_anonymous: false,
					created_at: nowText(),
					created_at_text: nowText(),
					...data
				}
				const list = getHeartMessageList()
				list.unshift(nextRecord)
				saveHeartMessageList(list)
				return {
					id: nextRecord._id
				}
			}
		)
	},

	async updateHeartMessage({ id, data } = {}) {
		return withMockFallback(
			async () => unwrapResponse(await http.put(apiUrls.heartMessages.byId(id), data)),
			async () => {
				const nextList = getHeartMessageList().map((item) =>
					item._id === normalizeText(id)
						? {
								...item,
								...data
							}
						: item
				)
				saveHeartMessageList(nextList)
				return {
					id: normalizeText(id)
				}
			}
		)
	},

	async removeHeartMessage({ id } = {}) {
		return withMockFallback(
			async () => unwrapResponse(await http.delete(apiUrls.heartMessages.byId(id))),
			async () => {
				saveHeartMessageList(getHeartMessageList().filter((item) => item._id !== normalizeText(id)))
				return {
					id: normalizeText(id)
				}
			}
		)
	},

	async getUserHeartMessageHome({ personnelId, keyword = '' } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.personnel.heartHome(personnelId), {
						params: {
							keyword
						}
					})
				),
			async () => listContactsForUser(normalizeText(personnelId), keyword)
		)
	},

	async listUserInboxLetters({ personnelId, keyword = '' } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.personnel.heartInbox(personnelId), {
						params: {
							keyword
						}
					})
				),
			async () => buildInboxList(normalizeText(personnelId), keyword)
		)
	},

	async getUserHeartMessageState({ personnelId } = {}) {
		return withMockFallback(
			async () => unwrapResponse(await http.get(apiUrls.personnel.heartState(personnelId))),
			async () => ({
				self: getPersonnelById(normalizeText(personnelId)),
				state: buildHeartbeatState(normalizeText(personnelId))
			})
		)
	},

	async listUserHeartMessages({ personnelId, contactId, since = '' } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.personnel.heartMessages(personnelId), {
						params: {
							contactId,
							since
						}
					})
				),
			async () => {
				const normalizedPersonnelId = normalizeText(personnelId)
				const normalizedContactId = normalizeText(contactId)
				const sourceList = getConversation(normalizedPersonnelId, normalizedContactId)
				const list = since
					? sourceList.filter(
							(item) => new Date(item.created_at).getTime() > new Date(since).getTime()
						)
					: sourceList
				const contact = getPersonnelById(normalizedContactId)
				return {
					self: getPersonnelById(normalizedPersonnelId),
					contact: contact
						? {
								_id: contact._id,
								name: contact.name,
								nickname: contact.nickname,
								personal_photo: contact.personal_photo,
								mbti: contact.mbti
							}
						: null,
					list,
					...buildCanSendState(normalizedPersonnelId, normalizedContactId)
				}
			}
		)
	},

	async sendUserHeartMessage({ personnelId, contactId, content } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.post(apiUrls.personnel.heartMessages(personnelId), {
						contactId,
						content
					})
				),
			async () => {
				const normalizedPersonnelId = normalizeText(personnelId)
				const normalizedContactId = normalizeText(contactId)
				const canSendState = buildCanSendState(normalizedPersonnelId, normalizedContactId)
				if (!canSendState.can_send) {
					throw new Error(canSendState.can_send_reason)
				}

				const nextMessage = {
					_id: ensureUniqueId('heart'),
					sender_record_id: normalizedPersonnelId,
					receiver_record_id: normalizedContactId,
					content: normalizeText(content),
					status: 'delivered',
					is_anonymous: false,
					quota_cost: 1,
					user_remark: '',
					created_at: nowText(),
					created_at_text: nowText()
				}

				const list = getHeartMessageList()
				list.push(nextMessage)
				saveHeartMessageList(list)

				const selfRecord = getPersonnelById(normalizedPersonnelId)
				if (selfRecord) {
					updatePersonnelRecord(normalizedPersonnelId, {
						remaining_heart_value: Math.max(0, toNumber(selfRecord.remaining_heart_value) - 1)
					})
				}

				return {
					id: nextMessage._id
				}
			}
		)
	},

	async getUserHeartPriorityBoard({ personnelId, __forceMock = false } = {}) {
		if (__forceMock) {
			return buildPriorityBoardResponse(normalizeText(personnelId))
		}

		return withMockFallback(
			async () => {
				const response = unwrapResponse(
					await http.get(apiUrls.personnel.heartPriorityBoard(personnelId))
				)
				const candidates =
					(response && (response.candidates || response.candidate_list || response.list)) || []

				// 接口成功但未返回候选数据时，自动回退 mock，避免前端列表为空。
				if (!Array.isArray(candidates) || !candidates.length) {
					return buildPriorityBoardResponse(normalizeText(personnelId))
				}
				return response
			},
			async () => buildPriorityBoardResponse(normalizeText(personnelId))
		)
	},

	async saveUserHeartPriorityBoard({ personnelId, orderedIds = [] } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.put(apiUrls.personnel.heartPriorityBoard(personnelId), {
						orderedIds
					})
				),
			async () => savePriorityBoardDraft(normalizeText(personnelId), orderedIds)
		)
	},

	async submitUserHeartPriorityBoard({ personnelId, orderedIds = [] } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.post(apiUrls.personnel.submitHeartPriorityBoard(personnelId), {
						orderedIds
					})
				),
			async () => submitPriorityBoard(normalizeText(personnelId), orderedIds)
		)
	},

	async listIntentPairRankings({ keyword = '', status = 'all', page = 1, pageSize = 5 } = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.intent.rankings(), {
						params: {
							keyword,
							status,
							page,
							pageSize
						}
					})
				),
			async () => {
				const sourceList = buildIntentRankingList()
					.filter((item) => (status === 'all' ? true : item.pair_status === status))
					.filter((item) =>
						normalizeKeyword(JSON.stringify(item)).includes(normalizeKeyword(keyword))
					)
				const pageData = paginateList(sourceList, page, pageSize)
				return {
					...pageData,
					stats: buildIntentStats(sourceList)
				}
			}
		)
	},

	async listIntentWeightedPairRankings({
		keyword = '',
		status = 'all',
		page = 1,
		pageSize = 5
	} = {}) {
		return withMockFallback(
			async () =>
				unwrapResponse(
					await http.get(apiUrls.intent.weightedRankings(), {
						params: {
							keyword,
							status,
							page,
							pageSize
						}
					})
				),
			async () => {
				const sourceList = buildWeightedRankingList()
					.filter((item) => (status === 'all' ? true : item.pair_status === status))
					.filter((item) =>
						normalizeKeyword(JSON.stringify(item)).includes(normalizeKeyword(keyword))
					)
				const pageData = paginateList(sourceList, page, pageSize)
				return {
					...pageData,
					stats: buildIntentStats(sourceList)
				}
			}
		)
	}
}
