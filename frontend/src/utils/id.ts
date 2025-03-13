import { v4 as uuidv4 } from "uuid"

export const generateUUID = () => {
  return crypto.randomUUID() // Built-in browser API (faster than uuid package)
}
