// Utilisation de Object.freeze() pour éviter les réallocations inutiles
export const CONSTANTS = Object.freeze({
  APPLICATION_TITLE: "AgentKit",
  LOGO_SRC: "/logo.png",
  LOGO_FULL_SRC: "/logo_full.png",
  LOGO_FULL_DARK_SRC: "/logo_full_dark.png",
})

// Exporter des constantes individuelles pour faciliter l'utilisation
export const { APPLICATION_TITLE, LOGO_SRC, LOGO_FULL_SRC, LOGO_FULL_DARK_SRC } = CONSTANTS
