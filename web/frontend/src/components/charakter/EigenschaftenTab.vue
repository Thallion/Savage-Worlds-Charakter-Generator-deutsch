<template>
  <v-card flat>
    <v-card-text>
      <v-row>
        <!-- Attribute -->
        <v-col cols="12" md="5">
          <h3 class="text-h6 mb-3">Attribute</h3>
          <v-card
            v-for="(attr, name) in daten.attribute"
            :key="name"
            variant="outlined"
            class="mb-2 pa-2"
          >
            <div class="d-flex align-center justify-space-between">
              <span class="text-body-1 font-weight-medium">{{ name }}</span>
              <div class="d-flex align-center ga-2">
                <v-btn
                  icon="mdi-minus"
                  size="small"
                  variant="outlined"
                  @click="store.spiellogikAktion('attribut/senken', String(name))"
                />
                <v-chip class="font-weight-bold" :color="wuerfelFarbe(attr.wert)">
                  {{ formatWuerfel(attr.wert, attr.modifier) }}
                </v-chip>
                <v-btn
                  icon="mdi-plus"
                  size="small"
                  variant="outlined"
                  color="primary"
                  @click="store.spiellogikAktion('attribut/steigern', String(name))"
                />
              </div>
            </div>
          </v-card>
        </v-col>

        <v-divider vertical class="mx-4 hidden-sm-and-down" />

        <!-- Fertigkeiten -->
        <v-col cols="12" md="6">
          <h3 class="text-h6 mb-3">Fertigkeiten</h3>
          <v-text-field
            v-model="sucheFertigkeit"
            label="Suchen..."
            density="compact"
            prepend-inner-icon="mdi-magnify"
            clearable
            class="mb-2"
          />
          <v-card
            v-for="(fert, name) in gefilterteFertigkeiten"
            :key="name"
            variant="outlined"
            class="mb-1 pa-2"
            density="compact"
          >
            <div class="d-flex align-center justify-space-between">
              <div>
                <span class="text-body-2 font-weight-medium">{{ name }}</span>
                <span class="text-caption text-grey ml-1">({{ fert.attribut }})</span>
                <v-chip v-if="fert.grundfertigkeit" size="x-small" class="ml-1">Grund</v-chip>
              </div>
              <div class="d-flex align-center ga-1">
                <v-btn
                  icon="mdi-minus"
                  size="x-small"
                  variant="outlined"
                  @click="store.spiellogikAktion('fertigkeit/senken', String(name))"
                />
                <v-chip
                  size="small"
                  class="font-weight-bold"
                  :color="wuerfelFarbe(fert.wuerfel?.value ?? 4)"
                >
                  {{ formatWuerfel(fert.wuerfel?.value ?? 4, fert.wuerfel?.modifier ?? 0) }}
                </v-chip>
                <v-btn
                  icon="mdi-plus"
                  size="x-small"
                  variant="outlined"
                  color="primary"
                  @click="store.spiellogikAktion('fertigkeit/steigern', String(name))"
                />
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCharakterStore } from '@/stores/charakter'

const store = useCharakterStore()
const sucheFertigkeit = ref('')

const daten = computed(() => store.aktuellerCharakter!.charakter_daten)

const gefilterteFertigkeiten = computed(() => {
  const all = daten.value.fertigkeiten || {}
  if (!sucheFertigkeit.value) return all
  const s = sucheFertigkeit.value.toLowerCase()
  const result: Record<string, any> = {}
  for (const [key, val] of Object.entries(all)) {
    if (key.toLowerCase().includes(s)) result[key] = val
  }
  return result
})

function formatWuerfel(wert: number, modifier: number): string {
  if (modifier > 0) return `W${wert}+${modifier}`
  if (modifier < 0) return `W${wert}${modifier}`
  return `W${wert}`
}

function wuerfelFarbe(wert: number): string {
  if (wert >= 12) return 'success'
  if (wert >= 8) return 'primary'
  if (wert >= 6) return 'info'
  return 'default'
}
</script>
