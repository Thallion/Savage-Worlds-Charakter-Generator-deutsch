import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'
import type { CharakterDaten, CharakterDetail, CharakterListItem } from '@/types/charakter'

export const useCharakterStore = defineStore('charakter', () => {
  const liste = ref<CharakterListItem[]>([])
  const aktuellerCharakter = ref<CharakterDetail | null>(null)
  const loading = ref(false)

  async function ladeListe() {
    loading.value = true
    try {
      liste.value = await api.get<CharakterListItem[]>('/charaktere')
    } finally {
      loading.value = false
    }
  }

  async function ladeCharakter(id: number) {
    loading.value = true
    try {
      aktuellerCharakter.value = await api.get<CharakterDetail>(`/charaktere/${id}`)
    } finally {
      loading.value = false
    }
  }

  async function erstelleCharakter(charName: string, settingName: string) {
    const charakter = await api.post<CharakterDetail>('/charaktere', {
      char_name: charName,
      active_setting_name: settingName,
    })
    await ladeListe()
    return charakter
  }

  async function speichereCharakter() {
    if (!aktuellerCharakter.value) return
    const id = aktuellerCharakter.value.id
    await api.put(`/charaktere/${id}`, {
      char_name: aktuellerCharakter.value.char_name,
      active_setting_name: aktuellerCharakter.value.active_setting_name,
      char_gen_completed: aktuellerCharakter.value.char_gen_completed,
      charakter_daten: aktuellerCharakter.value.charakter_daten,
    })
  }

  async function loescheCharakter(id: number) {
    await api.delete(`/charaktere/${id}`)
    await ladeListe()
  }

  async function spiellogikAktion(
    aktion: string,
    elementName?: string,
  ): Promise<{ success: boolean; message: string }> {
    if (!aktuellerCharakter.value) return { success: false, message: 'Kein Charakter geladen' }

    const result = await api.post<{
      success: boolean
      message: string
      charakter_daten?: CharakterDaten
    }>(`/spiellogik/${aktion}`, {
      charakter_daten: aktuellerCharakter.value.charakter_daten,
      element_name: elementName,
    })

    if (result.success && result.charakter_daten) {
      aktuellerCharakter.value.charakter_daten = result.charakter_daten
    }
    return result
  }

  return {
    liste,
    aktuellerCharakter,
    loading,
    ladeListe,
    ladeCharakter,
    erstelleCharakter,
    speichereCharakter,
    loescheCharakter,
    spiellogikAktion,
  }
})
