// ... existing imports ...
import { PWAInstallPrompt } from "./PWAInstallPrompt"

export const Layout = ({ children }: { children: React.ReactNode }) => {
  // ... existing code ...

  return (
    <div className="min-h-screen">
      {/* ... existing layout code ... */}
      {children}
      <PWAInstallPrompt />
    </div>
  )
}
