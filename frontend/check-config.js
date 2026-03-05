// Quick diagnostic to check environment variables
console.log('Environment Variables:')
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL)
console.log('All VITE_ vars:', Object.keys(import.meta.env).filter(k => k.startsWith('VITE_')))
