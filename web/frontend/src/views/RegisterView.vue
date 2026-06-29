<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="pa-4">
          <v-card-title class="text-h5 text-center">Registrieren</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleRegister">
              <v-text-field
                v-model="email"
                label="E-Mail"
                type="email"
                prepend-inner-icon="mdi-email"
                required
              />
              <v-text-field
                v-model="benutzername"
                label="Benutzername"
                prepend-inner-icon="mdi-account"
                required
              />
              <v-text-field
                v-model="passwort"
                label="Passwort"
                type="password"
                prepend-inner-icon="mdi-lock"
                required
              />
              <v-text-field
                v-model="passwortBestaetigung"
                label="Passwort bestätigen"
                type="password"
                prepend-inner-icon="mdi-lock-check"
                required
              />
              <v-alert v-if="error" type="error" class="mb-4" density="compact">
                {{ error }}
              </v-alert>
              <v-alert v-if="success" type="success" class="mb-4" density="compact">
                Registrierung erfolgreich! Du kannst dich jetzt anmelden.
              </v-alert>
              <v-btn type="submit" color="primary" block :loading="loading">
                Registrieren
              </v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions class="justify-center">
            <span class="text-body-2">Bereits registriert?</span>
            <v-btn variant="text" color="primary" to="/login">Anmelden</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const email = ref('')
const benutzername = ref('')
const passwort = ref('')
const passwortBestaetigung = ref('')
const error = ref('')
const success = ref(false)
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  success.value = false

  if (passwort.value !== passwortBestaetigung.value) {
    error.value = 'Passwörter stimmen nicht überein'
    return
  }

  loading.value = true
  try {
    await authStore.register(email.value, benutzername.value, passwort.value)
    success.value = true
  } catch (e: any) {
    error.value = e.message || 'Registrierung fehlgeschlagen'
  } finally {
    loading.value = false
  }
}
</script>
