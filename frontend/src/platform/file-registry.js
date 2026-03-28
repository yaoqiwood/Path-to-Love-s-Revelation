const selectedFileMap = new Map()

export function rememberSelectedFile(file) {
  const objectUrl = URL.createObjectURL(file)
  selectedFileMap.set(objectUrl, file)
  return objectUrl
}

export function getSelectedFile(filePath) {
  return selectedFileMap.get(filePath) || null
}

export function releaseSelectedFile(filePath) {
  if (!selectedFileMap.has(filePath)) {
    return
  }

  selectedFileMap.delete(filePath)
  URL.revokeObjectURL(filePath)
}
