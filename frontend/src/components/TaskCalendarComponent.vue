<template>
  <FullCalendar :events="calendarEvents" :options="options" />
</template>

<script setup>
import { computed } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
// Props for the component
const props = defineProps({
  rows: {
    type: Array,
    required: true,
  },
  onDateClick: {
    type: Function,
    required: true,
  },
  onEventClick: {
    type: Function,
    required: true,
  },
})

const calendarEvents = computed(() => transformEventsToFullCalendar(props.rows))

// Transform rows into FullCalendar events
function transformEventsToFullCalendar(datas) {
  return (
    datas?.map((event) => ({
      title: event.title,
      name: event.name,
      start: event.due_date,
      description: event.description,
      end: event.ends_on || null,
      color: event.event_color || '#3788d8', // Add a default or dynamic color
      backgroundColor: event.background_color || null, // Optional for further customization
      borderColor: event.border_color || null, // Optional for border customization
      textColor: event.text_color || null, // Optional for text customization
      extendedProps: {
        category: event.event_category,
        modified: event.modified,
        owner: event.owner,
      },
    })) || []
  )
}

// FullCalendar options
const options = computed(() => ({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay',
  },
  dateClick: props.onDateClick,
  eventClick: function (info) {
    const eventData = info.event

    props.onEventClick({ name: eventData.extendedProps.name })
  },
  editable: true,
  events: calendarEvents.value,
  droppable: true,
}))
</script>
