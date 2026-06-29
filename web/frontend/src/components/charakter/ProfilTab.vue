<template>
  <v-card flat>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="6">
          <v-text-field
            v-model="profil.Name"
            label="Name"
            @update:model-value="updateProfil"
          />
          <v-text-field
            v-model="profil.Konzept"
            label="Konzept"
            @update:model-value="updateProfil"
          />
          <v-text-field
            v-model="profil.Alter"
            label="Alter"
            @update:model-value="updateProfil"
          />
        </v-col>
        <v-col cols="12" md="6">
          <v-text-field
            v-model="profil.Geschlecht"
            label="Geschlecht"
            @update:model-value="updateProfil"
          />
          <v-text-field
            v-model="profil.Sprachen"
            label="Sprachen"
            @update:model-value="updateProfil"
          />
          <v-select
            :model-value="daten.active_setting_name"
            :items="einstellungenStore.verfuegbareSettings"
            item-title="name"
            item-value="name"
            label="Setting"
            @update:model-value="changeSetting"
          />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useCharakterStore } from '@/stores/charakter'
import { useEinstellungenStore } from '@/stores/einstellungen'

const store = useCharakterStore()
const einstellungenStore = useEinstellungenStore()

const daten = computed(() => store.aktuellerCharakter!.charakter_daten)
const profil = computed(() => daten.value.profil_daten)

function updateProfil() {
  daten.value.profil_daten = { ...profil.value }
}

async function changeSetting(name: string) {
  daten.value.active_setting_name = name
  store.aktuellerCharakter!.active_setting_name = name
  await einstellungenStore.ladeSetting(name)
}
</script>
