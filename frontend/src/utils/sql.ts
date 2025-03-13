import { type ExecutionResult } from "~/api-client"

export const getMessageFromExecutionResult = (result: ExecutionResult): string => {
  if (result.error) {
    return result.error
  }
  if (result.affectedRows) {
    return `${result.affectedRows} rows affected.`
  }
  return ""
}

const selectRegex = /^(SELECT|WITH)[\s\w\d\(\),.*<>=!%_\-+'":[\]|&]+$/i

export const checkStatementIsSelect = (statement: string): boolean => selectRegex.test(statement.trim())

export const filterNonFlattenedObjectFields = (rest: Record<string, any>) => {
  // Filters out any non-flattened fields. If needed, adjust.
  return Object.keys(rest).reduce(
    (acc: any, key: any) => (typeof rest[key] === "object" ? acc : { ...acc, [key]: rest[key] }),
    {}
  )
}
