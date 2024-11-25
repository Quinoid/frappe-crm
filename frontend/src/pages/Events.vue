<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Events" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="eventsListView?.customListActions"
        :actions="eventsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        class="bg-btn_primary"
        @click="handleCreateEvent"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="events"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Event"
    :options="{
      allowedViews: ['list', 'calendar'],
    }"
  />

  <div
    v-if="route.params.viewType === 'calendar'"
    class="flex flex-col h-full p-5 shadow-sm rounded-sm"
  >
    <CalendarComponent
      v-model="events"
      :rows="rows"
      :onDateClick="onDateClick"
      :onEventClick="onEventClick"
    />
  </div>

  <EventsListView
    ref="eventsListView"
    v-if="events.data && rows.length && route.params.viewType !== 'calendar'"
    v-model="events.data.page_length_count"
    v-model:list="events"
    :getRowRoute="getRowRoute"
    :rows="rows"
    :columns="events.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: events.data.row_count,
      totalCount: events.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
  />

  <div
    v-else-if="rows.length == 0 && route.params.value !== 'calendar'"
    class="flex h-full items-center justify-center"
  >
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
    >
      <ContactsIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Event')]) }}</span>
      <Button :label="__('Create')" @click="handleCreateEvent">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
  <EventModal
    v-model="showContactModal"
    v-model:quickEntry="showQuickEntryModal"
    :events="events"
    :key="componentKey"
    :event="editMode ? event : {}"
    :options="{ detailMode }"
  />
  <QuickEntryModal
    v-if="showQuickEntryModal"
    v-model="showQuickEntryModal"
    doctype="Event"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import EventsListView from '@/components/ListViews/EventsListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import { ref, computed } from 'vue'
import EventModal from '../components/Modals/EventModal.vue'
import QuickEntryModal from '../components/Modals/QuickEntryModal.vue'
import { useRoute } from 'vue-router'
import CalendarComponent from '@/components/CalendarComponent.vue'
import { createResource } from 'qbs-vue-ui'
const showContactModal = ref(false)
const showQuickEntryModal = ref(false)
const route = useRoute()

const eventsListView = ref(null)
const componentKey = ref(2)
// events data is loaded in the ViewControls component
const events = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)
const event = ref({})
const editMode = ref(false)
const detailMode = ref(false)

const rows = computed(() => {
  if (
    !events.value?.data?.data ||
    !['list', 'calendar'].includes(events.value.data.view_type)
  )
    return []
  return events.value?.data.data
})

function handleCreateEvent() {
  componentKey.value = componentKey.value + 1
  event.value = {}
  editMode.value = false
  setTimeout(() => {
    showContactModal.value = true
  }, 1000)
}
async function getRowRoute(row) {
  if (row) {
    editMode.value = true
    componentKey.value = componentKey.value + 1
    const resource = createResource({
      url: 'crm.api.events.custom_get_event_details',
      cache: ['event', row.name],
      params: {
        name: row.name,
      },
      auto: false, // Disable auto-fetch
      transform: (data) => ({
        ...data,
        subject: data.subject,
        starts_on: data.starts_on,
        ends_on: data.ends_on,
        color: data.color,
        event_category: data.event_category,
        event_type: data.event_type,
        participant: data.participant,
      }),
    })

    const data = await resource.fetch()
    event.value = data
    setTimeout(() => {
      detailMode.value = false
      showContactModal.value = true
    }, 1000)
  }
}
console.log(componentKey.value)
function onDateClick(arg) {
  console.log(arg)
}
function onEventClick(arg) {
  console.log(arg.name)
  getRowRoute(arg)
}
</script>
