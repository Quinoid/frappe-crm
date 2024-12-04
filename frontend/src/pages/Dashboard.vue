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
        <h3 class="text-lg font-semibold">Deals</h3>
        <p class="text-3xl font-bold text-red-600">
          {{ dashboardData?.deal_total_count }}
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
      <!-- Task List -->
      <div class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full">
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
          class="text-center text-gray-500 mt-4"
        >
          No tasks to display.
        </div>
      </div>
      <div class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full">
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
          class="text-center text-gray-500 mt-4"
        >
          No events to display.
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
      events: message?.events || [
        {
          name: 'EV00003',
          creation: '2024-11-08 09:38:22.367152',
          modified: '2024-11-08 09:38:22.367152',
          modified_by: 'arya.qbs@gmail.com',
          owner: 'arya.qbs@gmail.com',
          docstatus: 0,
          idx: 0,
          subject: 'New Event',
          event_category: 'Meeting',
          event_type: 'Public',
          color: null,
          send_reminder: 1,
          repeat_this_event: 0,
          starts_on: '2024-11-07 10:00:00',
          ends_on: '2024-11-20 12:00:00',
          status: 'Open',
          sender: null,
          all_day: 0,
          sync_with_google_calendar: 0,
          add_video_conferencing: 0,
          google_calendar: null,
          google_calendar_id: null,
          google_calendar_event_id: null,
          google_meet_link: null,
          pulled_from_google_calendar: 0,
          repeat_on: '',
          repeat_till: null,
          monday: 0,
          tuesday: 0,
          wednesday: 0,
          thursday: 0,
          friday: 0,
          saturday: 0,
          sunday: 0,
          description: 'Quarterly review meeting',
          _user_tags: null,
          _comments: null,
          _assign: null,
          _liked_by: null,
          _seen: null,
          custom_custom_color: null,
          custom_color: 'green',
        },
        {
          name: 'EV00004',
          creation: '2024-11-08 09:50:04.692949',
          modified: '2024-11-08 10:19:40.943920',
          modified_by: 'arya.qbs@gmail.com',
          owner: 'arya.qbs@gmail.com',
          docstatus: 0,
          idx: 0,
          subject: 'New Event2 renamed',
          event_category: 'Event',
          event_type: 'Private',
          color: null,
          send_reminder: 1,
          repeat_this_event: 0,
          starts_on: '2024-11-09 10:00:00',
          ends_on: '2024-11-25 12:00:00',
          status: 'Open',
          sender: null,
          all_day: 0,
          sync_with_google_calendar: 0,
          add_video_conferencing: 0,
          google_calendar: null,
          google_calendar_id: null,
          google_calendar_event_id: null,
          google_meet_link: null,
          pulled_from_google_calendar: 0,
          repeat_on: '',
          repeat_till: null,
          monday: 0,
          tuesday: 0,
          wednesday: 0,
          thursday: 0,
          friday: 0,
          saturday: 0,
          sunday: 0,
          description: 'Quarterly review meeting',
          _user_tags: null,
          _comments: null,
          _assign: null,
          _liked_by: null,
          _seen: '["arya.qbs@gmail.com"]',
          custom_custom_color: null,
          custom_color: 'violet',
        },
      ],
    }
  },
})

const dashboardData = computed(() => dashboardResource.data)
const isLoading = computed(() => dashboardResource.isLoading)
</script>
