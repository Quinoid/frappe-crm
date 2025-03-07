<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Organizations" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="organizationsListView?.customListActions"
        :actions="organizationsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        @click="showOrganizationModal = true"
        class="bg-btn_primary"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    @updateFilters="handleFilterUpdate"
    ref="viewControls"
    v-model="organizations"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Organization"
    :options="{
      allowedViews: ['list'],
    }"
  />
  <OrganizationsListView
    ref="organizationsListView"
    v-if="organizations.data && rows.length"
    v-model="organizations.data.page_length_count"
    v-model:list="organizations"
    :rows="rows"
    :columns="organizations.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: organizations.data.row_count,
      totalCount: organizations.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
  />
  <div
    v-else-if="organizations.data&& Object.keys(parentFilters).length === 0"
    class="flex h-full items-center justify-center"
  >
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
    >
      <OrganizationEmpty class="h-[196px] w-[196px] " />
      <span>{{ __('No {0} Found', [__('Organizations')]) }}</span>
                  <span class="text-gray-700 text-center font-inter text-sm font-normal leading-[20px]">{{'Strong businesses are built on strong partnerships. Organise, connect, and grow!' }}</span>  

      <Button :label="__('Add an Organisation!')" class="bg-btn_primary text-white" @click="showOrganizationModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
      
    </div>
  </div>
    <SearchEmptyComponent moduleName="Oraganizations" v-else-if="organizations.data && Object.keys(parentFilters).length > 0" :clearFunction="callChildFunction" />

  <OrganizationModal
    v-model="showOrganizationModal"
    v-model:quickEntry="showQuickEntryModal"
  />
  <QuickEntryModal
    v-if="showQuickEntryModal"
    v-model="showQuickEntryModal"
    doctype="CRM Organization"
  />
</template>
<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import OrganizationModal from '@/components/Modals/OrganizationModal.vue'
import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
import OrganizationsListView from '@/components/ListViews/OrganizationsListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import OrganizationEmpty from '@/components/Icons/OrganizationEmpty.vue'
import {
  dateFormat,
  dateTooltipFormat,
  timeAgo,
  website,
  formatNumberIntoCurrency,
} from '@/utils'
import { usersStore } from '@/stores/users'
import { ref, computed, onMounted } from 'vue'
import SearchEmptyComponent from '../components/SearchEmptyComponent.vue'
const { getUser } = usersStore()

const organizationsListView = ref(null)
const showOrganizationModal = ref(false)
const showQuickEntryModal = ref(false)

// organizations data is loaded in the ViewControls component
const organizations = ref({})
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
    !organizations.value?.data?.data ||
    !['list', 'group_by'].includes(organizations.value.data.view_type)
  )
    return []
  return organizations.value?.data.data.map((organization) => {
    let _rows = {}
    organizations.value?.data.rows.forEach((row) => {
      _rows[row] = organization[row]

      if (row === 'organization_name') {
        _rows[row] = {
          label: organization.organization_name,
          logo: organization.organization_logo,
        }
      }else if (row == '_assign') {
        let assignees = JSON.parse(organization._assign || '[]')
        _rows[row] = assignees.map((user) => ({
          name: user,
          image: getUser(user).user_image,
          label: getUser(user).full_name,
        }))
      } else if (row === 'website') {
        _rows[row] = website(organization.website)
      } else if (row === 'annual_revenue') {
        _rows[row] = formatNumberIntoCurrency(
          organization.annual_revenue,
          organization.currency,
        )
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: dateFormat(organization[row], dateTooltipFormat),
          timeAgo: __(timeAgo(organization[row])),
        }
      }
    })
    return _rows
  })
})
</script>
