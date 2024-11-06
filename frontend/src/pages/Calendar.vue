<template>
  <div
    v-if="!isLoading"
    class="flex flex-col h-full m-5 p-5 shadow-sm rounded-sm"
  >
    <Calendar :config="config" :events="calendarEvents">
      <template
        #header="{
          currentMonthYear,
          enabledModes,
          activeView,
          updateActiveView,
        }"
      >
        <div v-if="calendarEvents.length === 0" class="text-center">
          No events to display.
        </div>
        <div class="flex justify-between items-center mb-4 gap-3">
          <div class="flex gap-3 items-center">
            <select
              v-model="selectedMonth"
              class="px-2 py-1 border rounded-md text-lg font-bold"
              @change="handleMonthChange"
            >
              <option
                v-for="(month, index) in months"
                :key="index"
                :value="index"
              >
                {{ month }}
              </option>
            </select>
            <span class="font-bold">{{ currentYear }}</span>
          </div>
          <div class="flex gap-2 text-sm">
            <button
              v-for="mode in enabledModes"
              :key="mode"
              class="px-2 py-1 rounded-md hover:bg-gray-100 transition-all duration-300 ease-in-out"
              :class="{ 'font-bold': mode.label === activeView }"
              @click="updateActiveView(mode.label)"
            >
              {{ mode.label }}
            </button>
          </div>
        </div>
      </template>
    </Calendar>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { Calendar, createResource } from 'qbs-vue-ui'

export default {
  components: { Calendar },
  setup() {
    const isLoading = ref(true)
    const rawEvents = ref([])
    const config = ref({
      disableModes: [],
      defaultMode: 'Month',
      isEditMode: false,
      eventIcons: {},
      redundantCellHeight: 50,
      hourHeight: 50,
      enableShortcuts: true,
    })

    const currentMonth = ref(new Date().getMonth())
    const currentYear = ref(new Date().getFullYear())

    // List of month names
    const months = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ]

    const selectedMonth = ref(currentMonth.value)

    const getMonthRange = (month, year) => {
      const start = new Date(year, month, 1)
      const end = new Date(year, month + 1, 0)
      return {
        starts_on: start.toISOString().split('T')[0],
        ends_on: end.toISOString().split('T')[0],
      }
    }

    const { starts_on, ends_on } = getMonthRange(
      currentMonth.value,
      currentYear.value,
    )

    const eventsResource = createResource({
      url: 'crm.api.events.custom_list_events',
      cache: ['events', currentMonth.value, currentYear.value],
      params: {
        starts_on,
        ends_on,
      },
      auto: true,
      transform: (data) => {
        return data ? convertToCalendarData(data) : []
      },
    })

    function convertToCalendarData(events) {
      if (!Array.isArray(events)) {
        console.warn('Expected an array but got:', events)
        return []
      }
      return events.map((event) => ({
        id: event.name,
        title: event.subject || 'No Title',
        fromDate: event.starts_on,
        toDate: event.ends_on,
        description: event.description
          ? event.description.replace(/<\/?[^>]+(>|$)/g, '')
          : '',
        type: event.event_type,
        color: event.custom_color ?? 'green',
        isFullDay: Boolean(event.all_day),
        extendedProps: {
          owner: event.owner,
          status: event.status,
          sendReminder: event.send_reminder,
          repeatThisEvent: event.repeat_this_event,
          eventCategory: event.event_category,
          eventType: event.event_type,
          googleMeetLink: event.google_meet_link,
        },
      }))
    }

    const calendarEvents = computed(() => eventsResource.data)
    watch(
      () => eventsResource.loading,
      (loading) => (isLoading.value = loading),
    )

    // Handle changes in selected month
    const handleMonthChange = () => {
      currentMonth.value = selectedMonth.value
      eventsResource.fetch({
        starts_on: getMonthRange(currentMonth.value, currentYear.value)
          .starts_on,
        ends_on: getMonthRange(currentMonth.value, currentYear.value).ends_on,
      })
    }

    return {
      calendarEvents,
      config,
      isLoading,
      currentYear,
      selectedMonth,
      months,
      handleMonthChange,
    }
  },
}
</script>
