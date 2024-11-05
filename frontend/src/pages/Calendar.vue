<template>
  <div v-if="!isLoading" class="flex flex-col h-full p-2">
    <Calendar :config="config" :events="calendarEvents">
      <template
        #header="{
          currentMonthYear,
          enabledModes,
          activeView,
          decrement,
          increment,
          updateActiveView,
        }"
      >
        <div v-if="calendarEvents.length === 0" class="mt-4 text-center">
          No events to display.
        </div>
        <div class="flex justify-between items-center mb-4">
          <div class="flex gap-3 items-center">
            <button
              class="text-xl font-bold p-1 hover:bg-gray-100 transition-all duration-300 ease-in-out"
              @click="decrement"
            >
              {{ '<' }}
            </button>
            <span class="fornt-bold">{{ currentMonthYear }}</span>
            <button
              class="text-xl font-bold p-1 hover:bg-gray-100 transition-all duration-300 ease-in-out"
              @click="increment"
            >
              {{ '>' }}
            </button>
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
import { ref, computed } from 'vue'
import { Calendar } from 'qbs-vue-ui'

export default {
  components: { Calendar },
  setup() {
    const rawEvents = ref([])
    const isLoading = ref(true)
    const config = ref({
      disableModes: [],
      defaultMode: 'Month',
      isEditMode: false,
      eventIcons: {},
      redundantCellHeight: 50,
      hourHeight: 50,
      enableShortcuts: true,
    })

    async function fetchEvents() {
      try {
        const response = await fetch(
          'https://demo.qbsapps.com/api/resource/Event?fields=["*"]',
          {
            headers: {
              Authorization: 'token c4798018f59e3de:01b3a2e2f58cd1c', // Replace with your token if required
            },
          },
        )
        const data = await response.json()
        const convertedEvents = convertToCalendarData(data?.data || [])
        rawEvents.value = convertedEvents
        isLoading.value = false
      } catch (error) {
        isLoading.value = false
      }
    }

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
        color: event.color || '#3788d8',
        allDay: Boolean(event.all_day),
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

    const calendarEvents = computed(() => {
      return rawEvents.value
    })

    fetchEvents() // Call fetchEvents on component mount
    return { calendarEvents, config, isLoading }
  },
}
</script>
