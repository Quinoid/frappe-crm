<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>

  <div v-if="!isLoading" class="p-6 space-y-6">
    <!-- Dashboard Counts -->
    <div class="lg:w-3/5 grid grid-cols-1 sm:grid-cols-4 gap-6">
      <!-- Leads Card -->
      <div class="sm:col-span-1 bg-white shadow-md rounded-lg p-6 text-center">
        <h3 class="text-lg font-semibold">Leads</h3>
        <p class="text-3xl font-bold text-indigo-600">
          {{ dashboardData?.leadCount }}
        </p>
      </div>

      <!-- Deals Card -->
      <div class="sm:col-span-1 bg-white shadow-md rounded-lg p-6 text-center">
        <h3 class="text-lg font-semibold">Deals</h3>
        <p class="text-3xl font-bold text-green-600">
          {{ dashboardData?.dealCount }}
        </p>
      </div>

      <!-- Tasks Card -->
      <div class="sm:col-span-1 bg-white shadow-md rounded-lg p-6 text-center">
        <h3 class="text-lg font-semibold">Tasks</h3>
        <p class="text-3xl font-bold text-red-600">
          {{ dashboardData?.taskCount }}
        </p>
      </div>

      <div class="sm:col-span-1 bg-white shadow-md rounded-lg p-6 text-center">
        <h3 class="text-lg font-semibold">Contacts</h3>
        <p class="text-3xl font-bold text-purple-600">
          {{ dashboardData?.contact_total_count }}
        </p>
      </div>
    </div>

    <div class="flex-col gap-4 flex w-full lg:w-3/5">
      <!-- <FunnelChart />
      <BarChart /> -->
      <!-- Task List -->
      <div
        class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full max-h-[380px] overflow-y-auto"
      >
        <h3 class="text-lg font-medium mb-4 text-gray-900">Recent Tasks</h3>
        <ul>
          <li
            v-for="task in dashboardData?.tasks"
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
          v-if="dashboardData?.tasks?.length === 0"
          class="text-center text-gray-500 mt-4 p-3"
        >
          <div class="flex h-full items-center justify-center">
            <div
              class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
            >
              <TaskIcon class="h-10 w-10" />
              <span class="text-sm text-gray-500"> No tasks to display. </span>
            </div>
          </div>
        </div>
      </div>
      <!-- <LeadConversionReport />
      <DealConversionReportData /> -->
      <SaleFunnelReport />
      <!-- <TaskCompletionReport />
      <TeamPerformanceReport /> -->

      <div
        class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full max-h-[380px] overflow-y-auto"
      >
        <h3 class="text-lg font-medium mb-4 text-gray-900">Upcoming Events</h3>
        <ul>
          <li
            v-for="event in dashboardData?.events"
            :key="event.name"
            class="border-b last:border-none py-2"
          >
            <div class="flex justify-between items-center">
              <div>
                <p class="font-semibold">{{ event.subject }}</p>
                <p class="text-sm text-gray-500">{{ event.event_category }}</p>
                <p class="text-sm text-gray-500">
                  {{
                    event.starts_on
                      ? new Date(event.starts_on).toLocaleString()
                      : 'No Start Date'
                  }}
                </p>
              </div>

              <span
                :class="{
                  'bg-green-100 text-green-800': event.status === 'Open',
                  'bg-gray-100 text-gray-800': event.status === 'Closed',
                }"
                class="px-2 py-1 rounded-md text-xs"
              >
                {{ event.status }}
              </span>
            </div>
          </li>
        </ul>
        <div
          v-if="dashboardData?.events?.length === 0"
          class="text-center text-gray-500 mt-4 p-3"
        >
          <div class="flex h-full items-center justify-center">
            <div
              class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
            >
              <CalendarIcon class="h-10 w-10" />
              <span class="text-sm text-gray-500"> No Events to display. </span>
            </div>
          </div>
        </div>
      </div>
      <div
        v-if="callEnabled"
        class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full max-h-[380px] overflow-y-auto"
      >
        <h3 class="text-lg font-medium mb-4 text-gray-900">Call Logs</h3>
        <ul>
          <li
            v-for="calllog in dashboardData?.call_logs"
            :key="calllog.name"
            class="border-b last:border-none py-2"
          >
            <div class="flex justify-between items-center">
              <div>
                <p class="font-semibold">{{ calllog.caller }}</p>
                <p class="text-sm text-gray-500">
                  {{ calllog.medium }}
                </p>
                <p class="text-sm text-gray-500">
                  {{
                    calllog.creation
                      ? new Date(calllog.creation).toLocaleString()
                      : 'No Start Date'
                  }}
                </p>
              </div>

              <span
                :class="{
                  'bg-green-100 text-green-800': calllog.status === 'Open',
                  'bg-gray-100 text-gray-800': calllog.status === 'Closed',
                }"
                class="px-2 py-1 rounded-md text-xs"
              >
                {{ calllog.status }}
              </span>
            </div>
          </li>
        </ul>
        <div
          v-if="dashboardData?.call_logs?.length === 0"
          class="text-center text-gray-500 mt-4 p-3"
        >
          <div class="flex h-full items-center justify-center">
            <div
              class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
            >
              <PhoneIcon class="h-10 w-10" />
              <span class="text-sm text-gray-500">
                No Call Logs to display.
              </span>
            </div>
          </div>
        </div>
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
import CalendarIcon from '@/components/Icons/CalendarIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import { callEnabled } from '@/composables/settings'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
// import DealConversionReportData from '../components/Dashboard/DealConversionReportData.vue'
// import LeadConversionReport from '../components/Dashboard/LeadConversionReport.vue'
import SaleFunnelReport from '../components/Dashboard/SaleFunnelReport.vue'
// import TaskCompletionReport from '../components/Dashboard/TaskCompletionReport.vue'
// import TeamPerformanceReport from '../components/Dashboard/TeamPerformanceReport.vue'
let title = 'Dashboard'
const breadcrumbs = [{ label: title, route: { name: 'Dashboard' } }]

const dashboardResource = createResource({
  url: 'crm.api.dashboard.custom_dashboard',
  cache: ['dashboardCounts'],
  auto: true,
  transform: (data) => {
    const message = data || {}
    return {
      leadCount: message?.lead_total_count || 0,
      dealCount: message?.deal_total_count || 0,
      taskCount: message?.task_total_count || 0,
      eventCount: message?.event_total_count || 0,
      tasks: message?.tasks || [],
      events: message?.events,
      deal_total_count: message?.deal_total_count || 0,
      contact_total_count: message?.contact_total_count || 0,
      call_logs: message?.call_logs || [],
    }
  },
})

const dashboardData = computed(() => dashboardResource.data)
const isLoading = computed(() => dashboardResource.isLoading)
</script>
