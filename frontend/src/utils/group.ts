export const groupBy = (array: any[], key: string, defaultGroup = "default") => {
  const grouped = new Map<string, any[]>()
  
  array.forEach((item) => {
    const groupKey = item[key] ?? defaultGroup
    
    if (!grouped.has(groupKey)) grouped.set(groupKey, [])
    grouped.get(groupKey).push(item)
  })
  
  return Object.fromEntries(grouped)
}
