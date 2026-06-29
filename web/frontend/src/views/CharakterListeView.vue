<template>
  <v-container>
    <v-row class="mb-4" align="center">
      <v-col>
        <h1 class="text-h4">Meine Charaktere</h1>
      </v-col>
      <v-col cols="auto">
        <v-btn color="primary" prepend-icon="mdi-plus" @click="dialogOffen = true">
          Neuer Charakter
        </v-btn>
      </v-col>
    </v-row>

    <v-progress-linear v-if="store.loading" indeterminate color="primary" />

    <v-row v-if="store.liste.length === 0 && !store.loading">
      <v-col>
        <v-card class="pa-8 text-center">
          <v-icon size="64" color="grey">mdi-account-plus</v-icon>
          <p class="text-h6 mt-4">Noch keine Charaktere vorhanden</p>
          <p class="text-body-2 text-grey">Erstelle deinen ersten Charakter!</p>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col
        v-for="char in store.liste"
        :key="char.id"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card
          class="cursor-pointer"
          hover
          @click="router.push(`/charakter/${char.id}`)"
        >
          <v-card-title>{{ char.char_name || 'Unbenannt' }}</v-card-title>
          <v-card-subtitle>{{ char.active_setting_name }}</v-card-subtitle>
          <v-card-text>
            <v-chip
              :color="char.char_gen_completed ? 'success' : 'warning'"
              size="small"
            >
              {{ char.char_gen_completed ? 'Fertig' : 'In Bearbeitung' }}
            </v-chip>
            <span class="text-caption ml-2">
              {{ new Date(char.aktualisiert_am).toLocaleDateString('de-DE') }}
            </span>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn
              icon="mdi-delete"
              color="error"
              size="small"
              @click.stop="deleteChar(char.id)"
            />
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="dialogOffen" max-width="500">
      <v-card>
        <v-card-title>Neuer Charakter</v-card-title>
        <v-card-text>
          <v-text-field v-model="neuerName" label="Name" autofocus />
          <v-select
            v-model="neuesSetting"
            :items="einstellungenStore.verfuegbareSettings"
            item-title="name"
            item-value="name"
            label="Setting"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="dialogOffen = false">Abbrechen</v-btn>
          <v-btn color="primary" @click="erstelleNeuenCharakter">Erstellen</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCharakterStore } from '@/stores/charakter'
import { useEinstellungenStore } from '@/stores/einstellungen'

const router = useRouter()
const store = useCharakterStore()
const einstellungenStore = useEinstellungenStore()

const dialogOffen = ref(false)
const neuerName = ref('')
const neuesSetting = ref('SWAE')

onMounted(async () => {
  await Promise.all([store.ladeListe(), einstellungenStore.ladeSettings()])
})

async function erstelleNeuenCharakter() {
  if (!neuerName.value.trim()) return
  const charakter = await store.erstelleCharakter(neuerName.value, neuesSetting.value)
  dialogOffen.value = false
  neuerName.value = ''
  router.push(`/charakter/${charakter.id}`)
}

async function deleteChar(id: number) {
  if (confirm('Charakter wirklich löschen?')) {
    await store.loescheCharakter(id)
  }
}
</script>
