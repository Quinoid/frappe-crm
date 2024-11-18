<!-- <template>
  <div class="contents">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs
          :items="[{ label: 'Calendar', route: { name: 'Calendar' } }]"
        />
      </template>
    </LayoutHeader>
    <div
      v-if="!isLoading"
      class="flex flex-col h-full m-5 p-5 shadow-sm rounded-sm"
    >
      <Calendar
        :config="config"
        :events="calendarEvents"
        :create="createEvent"
        :update="updateEvent"
        :delete="deleteEvent"
        @dblclick="openCreateEventModal"
        :showCreateEventButton="true"
      >
        <template
          #header="{
            enabledModes,
            activeView,
            updateActiveView,
            createNewEventClick,
          }"
        >
          <div class="flex justify-between items-center mb-4 gap-3">
            <div class="flex gap-3 items-center">
              <select
                v-model="selectedMonth"
                class="px-2 py-1 border rounded-md !border-[#e8dcdc] text-lg font-bold min-w-[125px]"
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
              <button
                @click="createNewEventClick"
                class="px-2 py-1 font-semibold text-white bg-btn_primary rounded-md hover:bg-primary-600 transition-all duration-300 ease-in-out"
              >
                Create Event
              </button>
            </div>
          </div>
        </template>
      </Calendar>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { Calendar, createResource } from 'qbs-vue-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs } from 'qbs-vue-ui'
import { createToast } from '@/utils'
export default {
  components: { Calendar, LayoutHeader, Breadcrumbs },
  setup() {
    const isLoading = ref(true)
    const rawEvents = ref([])
    const isCreateEventModalOpen = ref(false) // Track modal visibility

    const openCreateEventModal = () => {
      isCreateEventModalOpen.value = true
    }

    const config = ref({
      disableModes: [],
      defaultMode: 'Month',
      isEditMode: true,
      eventIcons: {},
      redundantCellHeight: 50,
      hourHeight: 50,
      isDeletable: false,
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
    const createEventResource = createResource({
      url: 'crm.api.events.custom_create_event',
      method: 'post',
    })
    const updateEventResource = createResource({
      url: 'crm.api.events.custom_edit_event',
      method: 'post',
    })

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
        participant: event.custom_participant,
        venue: event.custom_venue,
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
    function appendTimeToDate(dateStr, timeStr) {
      // Format the Date object to "YYYY-MM-DD HH:MM:SS"
      const formattedDate = `${dateStr} ${timeStr}`

      return formattedDate
    }
    function transformEvent(event, update) {
      const {
        title,
        date,
        from_time,
        venue,
        participant,
        color,
        to_time,
        id,
        ...rest
      } = event
      console.log(event)
      // Create a new object with the transformed keys
      const transformedEvent = {
        subject: title, // title to subject
        starts_on: appendTimeToDate(date, from_time), // date to starts_on
        ends_on: appendTimeToDate(date, to_time), //
        custom_color: color, // color to custom_color
        from_time: from_time,
        name: update ? id : '',
        custom_participant: participant,
        custom_venue: venue,
        ...rest, // include the remaining properties as is
      }

      return transformedEvent
    }

    const createEvent = async (event) => {
      try {
        const newEvent = await createEventResource.fetch({
          ...transformEvent(event),
        })
        handleMonthChange() // Ensure this re-fetches the events
        createToast({
          title: newEvent.message,
          icon: 'check',
          iconClasses: 'text-green-600',
        })
        isCreateEventModalOpen.value = false // Close modal after creation
      } catch (error) {
        console.error('Error creating event:', error)
      }
    }

    const updateEvent = async (event) => {
      try {
        const newEvent = await updateEventResource.fetch({
          ...transformEvent(event, true),
        })

        isCreateEventModalOpen.value = false // Close modal after creation
        handleMonthChange() // Ensure this re-fetches the events
        createToast({
          title: newEvent.message,
          icon: 'check',
          iconClasses: 'text-green-600',
        })
      } catch (error) {
        console.error('Error creating event:', error)
      }
    }

    const deleteEvent = async (event) => {
      try {
        const response = await fetch(
          `crm.api.events.delete_event/${event.id}`,
          {
            method: 'DELETE',
          },
        )
        if (response.ok) {
          eventsResource.refresh()
          console.log('Event deleted:', event.id)
        } else {
          console.error('Failed to delete event')
        }
      } catch (error) {
        console.error('Error deleting event:', error)
      }
    }

    return {
      calendarEvents,
      config,
      isLoading,
      currentYear,
      selectedMonth,
      months,
      handleMonthChange,
      deleteEvent,
      updateEvent,
      createEvent,
      openCreateEventModal,
    }
  },
}
</script> -->
<template>
  <div class="contents">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs
          :items="[{ label: 'Calendar', route: { name: 'Calendar' } }]"
        />
      </template>
    </LayoutHeader>
    <div
      v-if="!isLoading"
      class="flex flex-col h-full m-5 p-5 shadow-sm rounded-sm"
    >
      <FullCalendar :events="calendarEvents" :options="calendarOptions" />
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs } from 'qbs-vue-ui'

export default {
  components: {
    FullCalendar,
    LayoutHeader,
    Breadcrumbs,
  },
  setup() {
    const isLoading = ref(true)
    const isCreateEventModalOpen = ref(false)

    // Flat array of events
    const calendarEvents = ref([
      {
        title: 'Meeting',
        start: '2024-11-13T10:37:47',
        end: '2024-11-19T10:37:51',
      },
      {
        title: 'Event',
        start: '2024-11-13T17:44:30',
        end: '2024-11-15T17:44:32',
      },
      {
        title: 'Other Event',
        start: '2024-11-12T17:40:30',
        end: '2024-11-13T17:40:32',
      },
      {
        title: 'Example',
        start: '2024-11-12T20:00:00',
        end: '2024-11-12T22:00:00',
      },
    ])

    const calendarOptions = ref({
      plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
      initialView: 'dayGridMonth',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay',
      },
      events: calendarEvents.value,
      dateClick(info) {
        console.log('Date clicked:', info.dateStr)
        isCreateEventModalOpen.value = true
      },
      eventClick(info) {
        console.log('Event clicked:', info.event)
      },
      editable: true,
      droppable: true,
    })

    return {
      calendarOptions,
      calendarEvents,
    }
  },
}
</script>
