<template>
  <v-card flat>
    <v-card-text>
      <v-row>
        <!-- Abgeleitete Werte -->
        <v-col cols="12" md="4">
          <h3 class="text-h6 mb-3">Abgeleitete Werte</h3>
          <v-card variant="outlined" class="mb-2 pa-3">
            <div class="d-flex justify-space-between">
              <span>Parade</span>
              <strong>{{ abgeleiteteWerte.parade }}</strong>
            </div>
          </v-card>
          <v-card variant="outlined" class="mb-2 pa-3">
            <div class="d-flex justify-space-between">
              <span>Robustheit</span>
              <strong>{{ abgeleiteteWerte.robustheit }}</strong>
            </div>
          </v-card>
          <v-card variant="outlined" class="mb-2 pa-3">
            <div class="d-flex justify-space-between">
              <span>Bewegungsweite</span>
              <strong>{{ abgeleiteteWerte.bewegungsweite }}</strong>
            </div>
          </v-card>
        </v-col>

        <!-- Profil-Zusammenfassung -->
        <v-col cols="12" md="4">
          <h3 class="text-h6 mb-3">Profil</h3>
          <v-table density="compact">
            <tbody>
              <tr v-for="(val, key) in daten.profil_daten" :key="key">
                <td class="font-weight-medium">{{ key }}</td>
                <td>{{ val }}</td>
              </tr>
              <tr>
                <td class="font-weight-medium">Setting</td>
                <td>{{ daten.active_setting_name }}</td>
              </tr>
              <tr>
                <td class="font-weight-medium">Volk</td>
                <td>{{ Object.keys(daten.voelker_selected || {}).join(', ') || '-' }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-col>

        <!-- Attribute Zusammenfassung -->
        <v-col cols="12" md="4">
          <h3 class="text-h6 mb-3">Attribute</h3>
          <v-table density="compact">
            <tbody>
              <tr v-for="(attr, name) in daten.attribute" :key="name">
                <td class="font-weight-medium">{{ name }}</td>
                <td>{{ formatWuerfel(attr.wert, attr.modifier) }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-col>
      </v-row>

      <v-row class="mt-4">
        <!-- Handicaps -->
        <v-col cols="12" md="4">
          <h3 class="text-h6 mb-3">Handicaps</h3>
          <v-chip
            v-for="h in daten.selected_handicaps"
            :key="h"
            class="mr-1 mb-1"
            color="accent"
          >
            {{ h }}
          </v-chip>
          <p v-if="!daten.selected_handicaps?.length" class="text-grey">Keine</p>
        </v-col>

        <!-- Talente -->
        <v-col cols="12" md="4">
          <h3 class="text-h6 mb-3">Talente</h3>
          <v-chip
            v-for="t in daten.selected_talente"
            :key="t"
            class="mr-1 mb-1"
            color="secondary"
          >
            {{ t }}
          </v-chip>
          <p v-if="!daten.selected_talente?.length" class="text-grey">Keine</p>
        </v-col>

        <!-- Fertigkeiten -->
        <v-col cols="12" md="4">
          <h3 class="text-h6 mb-3">Fertigkeiten</h3>
          <v-table density="compact">
            <tbody>
              <tr v-for="(fert, name) in aktiveFertigkeiten" :key="name">
                <td class="text-body-2">{{ name }}</td>
                <td>{{ formatWuerfel(fert.wuerfel?.value ?? 4, fert.wuerfel?.modifier ?? 0) }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useCharakterStore } from '@/stores/charakter'

const store = useCharakterStore()

const daten = computed(() => store.aktuellerCharakter!.charakter_daten)

const abgeleiteteWerte = computed(() => {
  const kon = daten.value.attribute?.Konstitution?.wert ?? 4
  const kaempfen = daten.value.fertigkeiten?.['Kämpfen']?.wuerfel?.value ?? 4
  return {
    parade: 2 + Math.floor(kaempfen / 2),
    robustheit: 2 + Math.floor(kon / 2),
    bewegungsweite: 6,
  }
})

const aktiveFertigkeiten = computed(() => {
  const all = daten.value.fertigkeiten || {}
  const result: Record<string, any> = {}
  for (const [key, val] of Object.entries(all)) {
    const f = val as any
    if (f.ausgewaehlt || f.grundfertigkeit) {
      result[key] = val
    }
  }
  return result
})

function formatWuerfel(wert: number, modifier: number): string {
  if (modifier > 0) return `W${wert}+${modifier}`
  if (modifier < 0) return `W${wert}${modifier}`
  return `W${wert}`
}
</script>
