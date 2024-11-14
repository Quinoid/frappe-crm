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
      <!-- <Button
        variant="solid"
        :label="__('Create')"
        class="bg-btn_primary"
        @click="showContactModal = true"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button> -->
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="events"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Event"
  />
  <EventsListView
    ref="eventsListView"
    v-if="events.data && rows.length"
    v-model="events.data.page_length_count"
    v-model:list="events"
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
  <div v-else-if="events.data" class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
    >
      <ContactsIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Event')]) }}</span>
      <Button :label="__('Create')" @click="showContactModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import EventsListView from '@/components/ListViews/EventsListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import { ref, computed } from 'vue'

const showContactModal = ref(false)
const showQuickEntryModal = ref(false)

const eventsListView = ref(null)

// events data is loaded in the ViewControls component
const events = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const rows = computed(() => {
  if (
    !events.value?.data?.data ||
    !['list', 'group_by'].includes(events.value.data.view_type)
  )
    return []
  return events.value?.data.data
})
</script>
