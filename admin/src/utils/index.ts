import { apiBaseURL } from '@/config'

const baseURL = apiBaseURL.replace(/\/api$/, '')

export function getFullVideoUrl(path: string): string {
    if (!path) return ''
    if (path.startsWith('http://') || path.startsWith('https://')) return path

    let cleanPath = path.replace(/^\//, '')
    if (!cleanPath.startsWith('storage/')) {
        cleanPath = `storage/${cleanPath}`
    }

    return `${baseURL}/${cleanPath}`
}

export function isImage(path: string): boolean {
    if (!path) return false
    const ext = path.split('.').pop()?.toLowerCase()
    return ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext || '')
}

export function isVideo(path: string): boolean {
    if (!path) return false
    const ext = path.split('.').pop()?.toLowerCase()
    return ['mp4', 'avi', 'mov', 'mkv', 'webm'].includes(ext || '')
}
