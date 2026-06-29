<template>
  <v-card flat>
    <v-card-text>
      <!-- Ausgewählte Talente -->
      <div v-if="selectedTalente.length" class="mb-4">
        <h3 class="text-subtitle-1 mb-2">Ausgewählt</h3>
        <v-chip
          v-for="name in selectedTalente"
          :key="name"
          closable
          color="secondary"
          class="mr-2 mb-2"
          @click:close="entferneTalent(name)"
        >
          {{ name }}
        </v-chip>
      </div>

      <v-text-field
        v-model="suche"
        label="Talent suchen..."
        prepend-inner-icon="mdi-magnify"
        clearable
        density="compact"
        class="mb-2"
      />

      <v-select
        v-model="rangFilter"
        :items="['Alle', 'Anfänger', 'Fortgeschritten', 'Veteran', 'Heroisch', 'Legendär']"
        label="Rang-Filter"
        density="compact"
        class="mb-2"
      />

      <v-list density="compact">
        <v-list-item
          v-for="(talent, name) in gefilterteTalente"
          :key="name"
          :disabled="selectedTalente.includes(String(name))"
          @click="waehleTalent(String(name))"
        >
          <template #prepend>
            <v-icon :color="selectedTalente.includes(String(name)) ? 'success' : ''">
              {{ selectedTalente.includes(String(name)) ? 'mdi-check-circle' : 'mdi-circle-outline' }}
            </v-icon>
          </template>
          <v-list-item-title>
            {{ talent.name || name }}
            <v-chip size="x-small" class="ml-1">{{ talent.rang }}</v-chip>
            <v-chip v-if="talent.kategorie" size="x-small" class="ml-1" variant="outlined">
              {{ talent.kategorie }}
            </v-chip>
          </v-list-item-title>
          <v-list-item-subtitle v-if="talent.voraussetzungen?.length" class="text-wrap">
            Voraussetzungen: {{ talent.voraussetzungen.join(', ') }}
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCharakterStore } from '@/stores/charakter'
import { useEinstellungenStore } from '@/stores/einstellungen'

const store = useCharakterStore()
const einstellungenStore = useEinstellungenStore()
const suche = ref('')
const rangFilter = ref('Alle')

const daten = computed(() => store.aktuellerCharakter!.charakter_daten)
const selectedTalente = computed(() => daten.value.selected_talente || [])

const talente = computed(() => einstellungenStore.aktuellesSetting?.talente ?? {})

const gefilterteTalente = computed(() => {
  const result: Record<string, any> = {}
  for (const [key, val] of Object.entries(talente.value)) {
    const t = val as any
    if (suche.value) {
      const s = suche.value.toLowerCase()
      if (!key.toLowerCase().includes(s) && !t.name?.toLowerCase().includes(s)) continue
    }
    if (rangFilter.value !== 'Alle' && t.rang !== rangFilter.value) continue
    result[key] = val
  }
  return result
})

async function waehleTalent(name: string) {
  await store.spiellogikAktion('talent/waehlen', name)
}

async function entferneTalent(name: string) {
  await store.spiellogikAktion('talent/entfernen', name)
}
</script>
