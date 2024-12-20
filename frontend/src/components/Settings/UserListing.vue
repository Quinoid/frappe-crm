<template>
  <div class="container mx-auto p-4 relative">
    <div class="overflow-auto max-h-[calc(100vh_-_10rem)]">
      <table class="min-w-full border-collapse border border-gray-300">
        <thead class="sticky top-0 bg-white z-10">
          <tr class="bg-table_header text-sm font-light text-gray-700">
            <th class="border border-gray-300 px-4 py-1 text-left">Name</th>
            <th class="border border-gray-300 px-4 py-1 text-left">Email</th>
            <th class="border border-gray-300 px-4 py-1 text-left">Roles</th>
            <th class="border border-gray-300 px-4 py-1 text-center">
              Enabled
            </th>
          </tr>
        </thead>
        <tbody v-if="users.length">
          <tr
            v-for="user in users"
            :key="user.email"
            class="text-sm font-normal"
          >
            <td class="border border-gray-300 px-4 py-1">{{ user.name }}</td>
            <td class="border border-gray-300 px-4 py-1">{{ user.email }}</td>
            <td class="border border-gray-300 px-4 py-1">
              <ul>
                <li v-for="role in user.roles" :key="role">{{ role }}</li>
              </ul>
            </td>
            <td class="border border-gray-300 px-4 py-1 text-center">
              <input
                type="checkbox"
                :checked="user.enabled"
                @change="toggleUser(user)"
                class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
            </td>
          </tr>
        </tbody>
        <div v-else class="text-center">
          <p class="text-gray-500">No users found</p>
        </div>
      </table>
    </div>
  </div>
</template>
<script setup>
import { call } from 'qbs-vue-ui'
import { ref } from 'vue'
import { createToast } from '@/utils'
async function getUserRoles() {
  const domain = window.location.hostname
  try {
    const res = await call('crm.api.dashboard.get_users_with_roles', {
      domain: domain,
    })
    users.value = res
  } catch (error) {
    console.log(error)
  }
}
getUserRoles()

const users = ref([])

async function toggleUser(user) {
  try {
    const res = await call('crm.api.dashboard.set_user_status', {
      enabled: user.enabled ? 0 : 1,
      user_email: user.email,
    })
    createToast({
      title: 'User Status Updated',
      position: 'bottom-center',
      text: res.message,
      icon: 'check',
      iconClasses: 'text-green-600',
    })
    getUserRoles()
  } catch (error) {
    console.log(error)
  }
}
</script>
