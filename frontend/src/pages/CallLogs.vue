<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Call Logs" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="callLogsListView?.customListActions"
        :actions="callLogsListView.customListActions"
      />
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="callLogs"
    @updateFilters="handleFilterUpdate"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Call Log"
  />
  <CallLogsListView
    ref="callLogsListView"
    v-if="callLogs.data && rows.length"
    v-model="callLogs.data.page_length_count"
    v-model:list="callLogs"
    :rows="rows"
    :columns="callLogs.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: callLogs.data.row_count,
      totalCount: callLogs.data.total_count,
    }"
    @showCallLog="showCallLog"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
  />
  <div
    v-else-if="callLogs.data&&Object.keys(parentFilters).length===0"
    class="flex h-full items-center justify-center"
  >
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
    >
      <CallLogsEmpty class="h-[196px] w-[196px] "  />
      <span>{{ __('No {0} Found', [__('Logs')]) }}</span>
    <span class="text-gray-700 text-center font-inter text-sm font-normal leading-[20px]">{{'Every conversation is a step closer to success! Track calls and stay in control.' }}</span>  
      <span class="text-sm text-gray-500">{{
        __('Setup Twilio account to enable phone calls ')
      }}</span>
      
    </div>
  </div>
    <SearchEmptyComponent moduleName="Logs" v-else-if="callLogs.data && Object.keys(parentFilters).length > 0" :clearFunction="callChildFunction" />

  <CallLogModal v-model="showCallLogModal" :name="selectedCallLog" />
</template>

<script setup>
import CustomActions from '@/components/CustomActions.vue'
import CallLogsEmpty from '@/components/Icons/CallLogEmpty.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import CallLogsListView from '@/components/ListViews/CallLogsListView.vue'
import CallLogModal from '@/components/Modals/CallLogModal.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import ViewControls from '@/components/ViewControls.vue'
import { getCallLogDetail } from '@/utils/callLog'
import { computed, ref,onMounted } from 'vue'
import SearchEmptyComponent from '../components/SearchEmptyComponent.vue'
const callLogsListView = ref(null)

// callLogs data is loaded in the ViewControls component
const callLogs = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)
const parentFilters = ref({});
const clearfilter = ref(null);

onMounted(() => {
  if (viewControls.value) {
    clearfilter.value = viewControls.value.clearfilter; // Capture the parent's function
  }
});

const callChildFunction = () => {
  if (clearfilter.value) {
    clearfilter.value();
  }
};

const handleFilterUpdate = (newFilters) => {
  parentFilters.value = { ...newFilters }; // Update the parent state
};
const rows = computed(() => {
  if (
    !callLogs.value?.data?.data ||
    !['list', 'group_by'].includes(callLogs.value.data.view_type)
  )
    return []
  return callLogs.value?.data.data.map((callLog) => {
    let _rows = {}
    callLogs.value?.data.rows.forEach((row) => {
      _rows[row] = getCallLogDetail(row, callLog)
    })
    return _rows
  })
})

const showCallLogModal = ref(false)
const selectedCallLog = ref(null)

function showCallLog(name) {
  selectedCallLog.value = name
  showCallLogModal.value = true
}
</script>
