<template>
  <v-container v-if="store.aktuellerCharakter" fluid>
    <v-row class="mb-2" align="center">
      <v-col cols="auto">
        <v-btn icon="mdi-arrow-left" variant="text" @click="router.push('/')" />
      </v-col>
      <v-col>
        <h2 class="text-h5">{{ daten.profil_daten?.Name || 'Neuer Charakter' }}</h2>
        <span class="text-caption">{{ store.aktuellerCharakter.active_setting_name }}</span>
      </v-col>
      <v-col cols="auto">
        <v-btn color="primary" prepend-icon="mdi-content-save" @click="speichern" :loading="saving">
          Speichern
        </v-btn>
      </v-col>
    </v-row>

    <!-- Punktebudget-Leiste -->
    <v-card class="mb-4" density="compact">
      <v-card-text class="d-flex ga-4 flex-wrap">
        <v-chip :color="(daten.verbleibende_attributsteigerungen ?? 5) > 0 ? 'primary' : 'success'">
          Attribute: {{ daten.verbleibende_attributsteigerungen ?? 5 }}
        </v-chip>
        <v-chip :color="(daten.verbleibende_fertigkeitssteigerungen ?? 12) > 0 ? 'primary' : 'success'">
          Fertigkeiten: {{ daten.verbleibende_fertigkeitssteigerungen ?? 12 }}
        </v-chip>
        <v-chip :color="(daten.gesamt_handicap_punkte ?? 0) < 4 ? 'primary' : 'success'">
          Handicap-Punkte: {{ daten.gesamt_handicap_punkte ?? 0 }} / 4
        </v-chip>
        <v-chip color="secondary">
          Talente: {{ daten.selected_talente?.length ?? 0 }}
        </v-chip>
      </v-card-text>
    </v-card>

    <v-tabs v-model="activeTab" color="primary" grow>
      <v-tab value="profil">Profil</v-tab>
      <v-tab value="voelker">Volk</v-tab>
      <v-tab value="eigenschaften">Eigenschaften</v-tab>
      <v-tab value="handicaps">Handicaps</v-tab>
      <v-tab value="talente">Talente</v-tab>
      <v-tab value="uebersicht">Übersicht</v-tab>
    </v-tabs>

    <v-tabs-window v-model="activeTab" class="mt-4">
      <v-tabs-window-item value="profil">
        <ProfilTab />
      </v-tabs-window-item>
      <v-tabs-window-item value="voelker">
        <VoelkerTab />
      </v-tabs-window-item>
      <v-tabs-window-item value="eigenschaften">
        <EigenschaftenTab />
      </v-tabs-window-item>
      <v-tabs-window-item value="handicaps">
        <HandicapsTab />
      </v-tabs-window-item>
      <v-tabs-window-item value="talente">
        <TalenteTab />
      </v-tabs-window-item>
      <v-tabs-window-item value="uebersicht">
        <UebersichtTab />
      </v-tabs-window-item>
    </v-tabs-window>
  </v-container>

  <v-container v-else class="text-center pa-8">
    <v-progress-circular indeterminate color="primary" size="64" />
    <p class="mt-4">Charakter wird geladen...</p>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCharakterStore } from '@/stores/charakter'
import { useEinstellungenStore } from '@/stores/einstellungen'
import ProfilTab from '@/components/charakter/ProfilTab.vue'
import VoelkerTab from '@/components/charakter/VoelkerTab.vue'
import EigenschaftenTab from '@/components/charakter/EigenschaftenTab.vue'
import HandicapsTab from '@/components/charakter/HandicapsTab.vue'
import TalenteTab from '@/components/charakter/TalenteTab.vue'
import UebersichtTab from '@/components/charakter/UebersichtTab.vue'

const route = useRoute()
const router = useRouter()
const store = useCharakterStore()
const einstellungenStore = useEinstellungenStore()

const activeTab = ref('profil')
const saving = ref(false)

const daten = computed(() => store.aktuellerCharakter?.charakter_daten ?? ({} as any))

onMounted(async () => {
  const id = Number(route.params.id)
  await store.ladeCharakter(id)
  if (store.aktuellerCharakter) {
    await einstellungenStore.ladeSetting(store.aktuellerCharakter.active_setting_name)
  }
})

async function speichern() {
  saving.value = true
  try {
    await store.speichereCharakter()
  } finally {
    saving.value = false
  }
}
</script>
