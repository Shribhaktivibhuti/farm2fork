/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_API_TIMEOUT: string
  readonly VITE_AWS_REGION: string
  readonly VITE_S3_BUCKET_NAME: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_ENABLE_PWA: string
  readonly VITE_ENABLE_OFFLINE_MODE: string
  readonly VITE_SUPPORTED_LANGUAGES: string
  readonly VITE_DEFAULT_LANGUAGE: string
  readonly VITE_DEMO_MODE: string
  readonly VITE_DEMO_OTP: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
