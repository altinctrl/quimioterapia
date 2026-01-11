/// <reference types="vite/client" />

interface ImportMetaEnv {
	readonly DEV?: boolean
	readonly VITE_ENABLE_FARMACIA_MOCK?: string
}

interface ImportMeta {
	readonly env: ImportMetaEnv
}
