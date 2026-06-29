import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'

interface SettingListItem {
  name: string
  datei: string
}

export const useEinstellungenStore = defineStore('einstellungen', () => {
  const verfuegbareSettings = ref<SettingListItem[]>([])
  const aktuellesSetting = ref<Record<string, any> | null>(null)
  const loading = ref(false)

  async function ladeSettings() {
    verfuegbareSettings.value = await api.get<SettingListItem[]>('/settings')
  }

  async function ladeSetting(name: string) {
    loading.value = true
    try {
      aktuellesSetting.value = await api.get<Record<string, any>>(`/settings/${name}`)
    } finally {
      loading.value = false
    }
  }

  return { verfuegbareSettings, aktuellesSetting, loading, ladeSettings, ladeSetting }
})
