<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Emails" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="communicationListView?.customListActions"
        :actions="communicationListView.customListActions"
      />
      <!-- <Button
        variant="solid"
        :label="__('Create')"
        class="bg-btn_primary"
        @click="handleCreateEvent"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button> -->
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="communications"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Communication"
    :options="{
      allowedViews: ['list'],
    }"
  />

  <CommunicationListView
    ref="communicationListView"
    v-if="
      communications.data && rows.length && route.params.viewType !== 'calendar'
    "
    v-model="communications.data.page_length_count"
    v-model:list="communications"
    :rows="rows"
    :columns="communications.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: communications.data.row_count,
      totalCount: communications.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
  />

  <div
    v-else-if="communications.data"
    class="flex h-full items-center justify-center"
  >
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
    >
      <ContactsIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Emails')]) }}</span>
      <span class="text-sm text-gray-500">{{
        __('Setup Email account to enable accessing your emails from here')
      }}</span>
    </div>
  </div>

  <QuickEntryModal
    v-if="showQuickEntryModal"
    v-model="showQuickEntryModal"
    doctype="Communication"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import { ref, computed } from 'vue'
import CommunicationListView from '../components/ListViews/CommunicationListView.vue'
import QuickEntryModal from '../components/Modals/QuickEntryModal.vue'
import { useRoute } from 'vue-router'
const showQuickEntryModal = ref(false)
const route = useRoute()

const communicationListView = ref(null)
// communications data is loaded in the ViewControls component
const communications = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const rows = computed(() => {
  if (
    !communications.value?.data?.data ||
    !['list'].includes(communications.value.data.view_type)
  )
    return []
  return communications.value?.data.data
})
</script>
