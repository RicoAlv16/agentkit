import { useEffect, useState } from 'react'
import { FaDownload } from 'react-icons/fa'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>
}

export const PWAInstallPrompt = () => {
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [isInstalled, setIsInstalled] = useState(false)

  useEffect(() => {
    // Vérifier si l'application est déjà installée
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true)
      return
    }

    const handleBeforeInstallPrompt = (e: Event) => {
      // Empêcher Chrome 67+ d'afficher automatiquement la fenêtre d'installation
      e.preventDefault()
      // Stocker l'événement pour pouvoir le déclencher plus tard
      setInstallPrompt(e as BeforeInstallPromptEvent)
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    }
  }, [])

  const handleInstallClick = async () => {
    if (!installPrompt) return

    // Afficher la fenêtre d'installation
    await installPrompt.prompt()

    // Attendre la réponse de l'utilisateur
    const choiceResult = await installPrompt.userChoice

    // Réinitialiser l'état
    setInstallPrompt(null)

    if (choiceResult.outcome === 'accepted') {
      console.log('L\'utilisateur a accepté l\'installation')
      setIsInstalled(true)
    } else {
      console.log('L\'utilisateur a refusé l\'installation')
    }
  }

  if (isInstalled || !installPrompt) return null

  return (
    <button
      onClick={handleInstallClick}
      className="fixed bottom-4 right-4 flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-white shadow-lg"
    >
      <FaDownload />
      <span>Installer l'application</span>
    </button>
  )
}