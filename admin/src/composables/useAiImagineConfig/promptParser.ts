import { CONTENT_SETTING_PRESETS } from './types'
import type { ContentSetting } from './types'

/** 已知的内容设定 key 集合 */
const KNOWN_SETTING_KEYS = new Set(CONTENT_SETTING_PRESETS.map(p => p.key))

/** 从 key 查找预设 label */
function findPresetLabel(key: string): string | undefined {
  return CONTENT_SETTING_PRESETS.find(p => p.key === key)?.label
}

export interface ParsedPromptResult {
  userPrompt: string
  contentSettings: ContentSetting[]
}

/**
 * 解析带标签的提示词文本。
 * - [brief] 标签内容 → userPrompt
 * - 已知标签 (character/position/style/scene/camera/emotion) → contentSettings
 * - 未知标签或无标签内容 → 追加到 userPrompt
 */
export function parseTaggedPrompt(text: string): ParsedPromptResult {
  const tagPattern = /^\[(\w+)\]:\s*/
  const lines = text.split('\n')

  // 收集各标签内容
  const sections: { tag: string; content: string }[] = []
  let currentTag: string | null = null
  let currentLines: string[] = []

  for (const line of lines) {
    const match = line.match(tagPattern)
    if (match) {
      // 保存上一段
      if (currentTag !== null) {
        sections.push({ tag: currentTag, content: currentLines.join('\n').trim() })
      }
      currentTag = match[1]!
      currentLines = [line.replace(tagPattern, '')]
    } else {
      currentLines.push(line)
    }
  }
  // 保存最后一段
  if (currentTag !== null) {
    sections.push({ tag: currentTag, content: currentLines.join('\n').trim() })
  }

  // 如果没有解析到任何标签，则整段文本作为 userPrompt
  if (sections.length === 0) {
    return { userPrompt: text.trim(), contentSettings: [] }
  }

  // 分类：brief → userPrompt，已知标签 → contentSettings，其余 → 追加到 userPrompt
  let userPrompt = ''
  const extraLines: string[] = []
  const newSettings: ContentSetting[] = []

  for (const sec of sections) {
    if (sec.tag === 'brief') {
      userPrompt = sec.content
    } else if (KNOWN_SETTING_KEYS.has(sec.tag)) {
      const label = findPresetLabel(sec.tag)!
      newSettings.push({ label, key: sec.tag, content: sec.content })
    } else {
      // 未知标签 → 原样追加到主提示词
      extraLines.push(`[${sec.tag}]: ${sec.content}`)
    }
  }

  if (extraLines.length > 0) {
    userPrompt = userPrompt
      ? userPrompt + '\n' + extraLines.join('\n')
      : extraLines.join('\n')
  }

  return { userPrompt, contentSettings: newSettings }
}
