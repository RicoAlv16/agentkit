// Ce fichier sera copié tel quel dans le dossier public
// Vous pouvez ajouter ici des gestionnaires d'événements personnalisés pour votre service worker

self.addEventListener('install', (event) => {
  console.log('Service Worker installing.');
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activating.');
});

// Vous pouvez ajouter d'autres gestionnaires d'événements ici