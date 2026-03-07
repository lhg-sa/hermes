<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold text-gray-800">Hermes</h1>
        <button
          @click="handleLogout"
          class="text-sm text-red-600 hover:text-red-800"
        >
          Cerrar sesión
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 py-8">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">
          Bienvenido, {{ user }}
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-blue-50 rounded-lg p-4">
            <p class="text-sm text-blue-600 font-medium">Estado</p>
            <p class="text-2xl font-bold text-blue-800">Activo</p>
          </div>
          <div class="bg-green-50 rounded-lg p-4">
            <p class="text-sm text-green-600 font-medium">Sesión</p>
            <p class="text-2xl font-bold text-green-800">Válida</p>
          </div>
          <div class="bg-purple-50 rounded-lg p-4">
            <p class="text-sm text-purple-600 font-medium">App</p>
            <p class="text-2xl font-bold text-purple-800">Hermes</p>
          </div>
        </div>

        <div class="mt-6 p-4 bg-gray-50 rounded-lg">
          <p class="text-sm text-gray-600">
            Esta es una vista de ejemplo. Aquí puedes agregar más funcionalidades según tus necesidades.
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref('')

onMounted(() => {
  user.value = localStorage.getItem('hermes_user') || 'Usuario'
})

const handleLogout = () => {
  localStorage.removeItem('hermes_token')
  localStorage.removeItem('hermes_user')
  router.push('/login')
}
</script>
