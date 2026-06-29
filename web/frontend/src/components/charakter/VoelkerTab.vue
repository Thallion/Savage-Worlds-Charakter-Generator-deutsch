<template>
  <v-card flat>
    <v-card-text>
      <v-alert v-if="selectedVolk" type="info" class="mb-4" density="compact" closable>
        Gewähltes Volk: <strong>{{ selectedVolk }}</strong>
      </v-alert>

      <v-text-field
        v-model="suche"
        label="Volk suchen..."
        prepend-inner-icon="mdi-magnify"
        clearable
        class="mb-4"
      />

      <v-row>
        <v-col
          v-for="(volk, name) in gefilterteVoelker"
          :key="name"
          cols="12"
          sm="6"
          md="4"
        >
          <v-card
            :color="selectedVolk === name ? 'primary' : undefined"
            :variant="selectedVolk === name ? 'elevated' : 'outlined'"
            hover
            @click="waehleVolk(String(name))"
          >
            <v-card-title class="text-body-1">{{ volk.name || name }}</v-card-title>
            <v-card-text>
              <div v-if="volk.besonderheiten?.length" class="text-caption">
                <strong>Besonderheiten:</strong>
                <ul class="ml-4">
                  <li v-for="b in volk.besonderheiten.slice(0, 3)" :key="b">{{ b }}</li>
                  <li v-if="volk.besonderheiten.length > 3">
                    ... und {{ volk.besonderheiten.length - 3 }} weitere
                  </li>
                </ul>
              </div>
              <div v-if="volk.handicaps?.length" class="text-caption mt-1">
                <strong>Handicaps:</strong> {{ volk.handicaps.join(', ') }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-alert v-if="Object.keys(gefilterteVoelker).length === 0" type="warning" class="mt-4">
        Keine Völker gefunden.
      </v-alert>
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

const daten = computed(() => store.aktuellerCharakter!.charakter_daten)
const selectedVolk = computed(() => {
  const keys = Object.keys(daten.value.voelker_selected || {})
  return keys.length > 0 ? keys[0] : null
})

const voelker = computed(() => einstellungenStore.aktuellesSetting?.voelker ?? {})

const gefilterteVoelker = computed(() => {
  if (!suche.value) return voelker.value
  const s = suche.value.toLowerCase()
  const result: Record<string, any> = {}
  for (const [key, val] of Object.entries(voelker.value)) {
    if (key.toLowerCase().includes(s) || (val as any).name?.toLowerCase().includes(s)) {
      result[key] = val
    }
  }
  return result
})

async function waehleVolk(name: string) {
  await store.spiellogikAktion('volk/waehlen', name)
}
</script>
