import {onMounted, onUnmounted, ref} from 'vue'
import {useDocumentVisibility} from '@vueuse/core'

interface AutoRefreshOptions {
  intervaloPadrao?: number
  intervaloRetry?: number
  condicoesPausa?: Array<() => boolean>
}

export function useAutoRefresh(fetchFunction: () => Promise<void>, options: AutoRefreshOptions = {}) {
  const {
    intervaloPadrao = 60000,
    intervaloRetry = 2500,
    condicoesPausa = []
  } = options

  const timer = ref<ReturnType<typeof setInterval> | null>(null)
  const isRetrying = ref(false)
  const isTabVisible = useDocumentVisibility()

  const isUserTyping = () => {
    const active = document.activeElement
    return active && (
      active.tagName === 'INPUT' ||
      active.tagName === 'TEXTAREA' ||
      active.tagName === 'SELECT'
    )
  }

  const isBlocked = () => {
    if (isTabVisible.value === 'hidden') return true
    if (isUserTyping()) return true
    if (condicoesPausa.some(cond => cond())) return true
    return false
  }

  const runCycle = async () => {
    if (isBlocked()) {
      if (!isRetrying.value) {
        setTimer(intervaloRetry)
        isRetrying.value = true
      }
      return
    }

    try {
      await fetchFunction()
    } catch (error) {
      console.error('Erro no auto-refresh:', error)
    } finally {
      if (isRetrying.value) {
        setTimer(intervaloPadrao)
        isRetrying.value = false
      }
    }
  }

  const setTimer = (ms: number) => {
    stop()
    timer.value = setInterval(runCycle, ms)
  }

  const start = () => {
    setTimer(intervaloPadrao)
  }

  const stop = () => {
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }
  }

  onMounted(() => start())
  onUnmounted(() => stop())

  return {start, stop}
}
