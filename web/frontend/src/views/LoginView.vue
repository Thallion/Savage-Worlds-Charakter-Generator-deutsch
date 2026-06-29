<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="pa-4">
          <v-card-title class="text-h5 text-center">Anmelden</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="email"
                label="E-Mail"
                type="email"
                prepend-inner-icon="mdi-email"
                required
              />
              <v-text-field
                v-model="passwort"
                label="Passwort"
                type="password"
                prepend-inner-icon="mdi-lock"
                required
              />
              <v-alert v-if="error" type="error" class="mb-4" density="compact">
                {{ error }}
              </v-alert>
              <v-btn type="submit" color="primary" block :loading="loading">
                Anmelden
              </v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions class="justify-center">
            <span class="text-body-2">Noch kein Konto?</span>
            <v-btn variant="text" color="primary" to="/register">Registrieren</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const passwort = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, passwort.value)
    router.push('/')
  } catch (e: any) {
    error.value = e.message || 'Anmeldung fehlgeschlagen'
  } finally {
    loading.value = false
  }
}
</script>
