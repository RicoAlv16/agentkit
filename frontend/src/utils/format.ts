// Mettre en cache l'instance Intl.DateTimeFormat pour la réutiliser
const dateFormatter = new Intl.DateTimeFormat("en-US")

export const formatDate = (dateString: string): string => {
  if (!dateString) return ""
  
  // Utiliser Date.parse qui est plus efficace que "new Date()"
  const timestamp = Date.parse(dateString) // More efficient than "new Date()"
  if (isNaN(timestamp)) return "" // Handle invalid dates safely
  
  return dateFormatter.format(timestamp)
}
