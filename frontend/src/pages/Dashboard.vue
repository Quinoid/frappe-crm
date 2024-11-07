<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>

  <div v-if="!isLoading" class="p-6 space-y-6">
    <!-- Dashboard Counts -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <!-- Leads Card -->
      <div class="bg-white shadow-md rounded-lg p-6 text-center">
        <h3 class="text-lg font-semibold">Leads</h3>
        <p class="text-3xl font-bold text-indigo-600">
          {{ dashboardData.value.leadCount }}
        </p>
      </div>

      <!-- Deals Card -->
      <div class="bg-white shadow-md rounded-lg p-6 text-center">
        <h3 class="text-lg font-semibold">Deals</h3>
        <p class="text-3xl font-bold text-green-600">
          {{ dashboardData.value.dealCount }}
        </p>
      </div>

      <!-- Tasks Card -->
      <div class="bg-white shadow-md rounded-lg p-6 text-center">
        <h3 class="text-lg font-semibold">Tasks</h3>
        <p class="text-3xl font-bold text-red-600">
          {{ dashboardData.value.taskCount }}
        </p>
      </div>
    </div>

    <!-- Task List -->
    <div class="bg-white shadow-md rounded-lg p-6">
      <h3 class="text-lg font-semibold mb-4">Recent Tasks</h3>
      <ul>
        <li
          v-for="task in dashboardData.value.tasks"
          :key="task.name"
          class="border-b last:border-none py-2"
        >
          <div class="flex justify-between items-center">
            <div>
              <p class="font-semibold">{{ task.title }}</p>
              <p class="text-sm text-gray-500">
                {{
                  task.due_date
                    ? new Date(task.due_date).toLocaleString()
                    : 'No Due Date'
                }}
              </p>
            </div>
            <span
              :class="{
                'bg-yellow-100 text-yellow-800': task.priority === 'Low',
                'bg-blue-100 text-blue-800': task.priority === 'Medium',
                'bg-red-100 text-red-800': task.priority === 'High',
              }"
              class="px-2 py-1 rounded-md text-xs"
            >
              {{ task.priority }}
            </span>
          </div>
        </li>
      </ul>
      <div
        v-if="dashboardData.value.tasks.length === 0"
        class="text-center text-gray-500 mt-4"
      >
        No tasks to display.
      </div>
    </div>
  </div>

  <div v-else class="flex justify-center items-center h-full text-gray-500">
    Loading data...
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, createResource } from 'qbs-vue-ui'

let title = 'Dashboard'
const breadcrumbs = [{ label: title, route: { name: 'Dashboard' } }]

const dashboardResource = createResource({
  url: 'crm.api.dashboard.custom_dashboard',
  cache: ['dashboardCounts'],
  auto: true,
  transform: (data) => {
    const message = data?.message || {}
    return {
      leadCount: message.lead_total_count || 0,
      dealCount: message.deal_total_count || 0,
      taskCount: message.task_total_count || 0,
      tasks: message.tasks || [],
    }
  },
})

const dashboardData = computed(() => dashboardResource.data)
const isLoading = computed(() => dashboardResource.isLoading)
</script>
