<script lang="ts" setup>
import {Toaster} from '@/components/ui/sonner'
</script>

<template>
  <router-view/>
  <Toaster :style="{ zIndex: 9999 }" closeButton position="top-right" richColors/>
</template>


<style>
/* --- FIX GLOBAL PARA O TOAST (SONNER) --- */
:where([data-sonner-toaster]) {
  position: fixed !important;
  top: 0 !important;
  right: 0 !important;
  bottom: auto !important;
  left: auto !important;
  z-index: 99999 !important;

  width: auto !important;
  max-width: 100vw !important;
  padding: 24px !important;
  gap: 12px !important;

  display: flex !important;
  flex-direction: column !important;
  align-items: flex-end !important;
  pointer-events: none;
}

:where([data-sonner-toast]) {
  position: relative !important;
  pointer-events: auto !important;
  opacity: 1 !important;
  visibility: visible !important;
  z-index: 99999 !important;

  width: 360px !important;
  min-height: auto !important;
  box-sizing: border-box !important;

  display: flex !important;
  align-items: center !important;
  gap: 12px !important;

  padding: 16px 56px 16px 16px !important;

  background-color: white !important;
  color: #1f2937 !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;

  transform: none !important;
  left: auto !important;
  right: auto !important;
}

[data-sonner-toast][data-type="success"] {
  border-left: 5px solid #22c55e !important;
  background-color: #ffffff !important;
}

[data-sonner-toast][data-type="success"] svg {
  color: #16a34a !important;
  width: 20px !important;
  height: 20px !important;
}

[data-sonner-toast][data-type="error"] {
  border-left: 5px solid #ef4444 !important;
}

[data-sonner-toast][data-type="error"] svg {
  color: #dc2626 !important;
  width: 20px !important;
  height: 20px !important;
}

[data-sonner-toast][data-type="info"] {
  border-left: 5px solid #3b82f6 !important;
}

[data-sonner-toast][data-type="info"] svg {
  color: #2563eb !important;
  width: 20px !important;
  height: 20px !important;
}

[data-sonner-toast][data-type="warning"] {
  border-left: 5px solid #eab308 !important;
}

[data-sonner-toast] [data-content] {
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  gap: 2px !important;
}

[data-sonner-toast] [data-title] {
  font-weight: 600 !important;
  font-size: 14px !important;
  line-height: 1.2 !important;
}

[data-sonner-toast] [data-description] {
  color: #6b7280 !important;
  font-size: 13px !important;
  line-height: 1.4 !important;
  margin: 0 !important;
}

[data-sonner-toast] [data-close-button] {
  position: absolute !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  right: 12px !important;

  width: 24px !important;
  height: 24px !important;

  background: transparent !important;
  border: none !important;
  cursor: pointer !important;
  color: #9ca3af !important;

  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 0 !important;
  margin: 0 !important;
  border-radius: 4px !important;
  transition: background 0.2s !important;
}

[data-sonner-toast] [data-close-button]:hover {
  color: #111827 !important;
  background-color: #f3f4f6 !important;
}
</style>