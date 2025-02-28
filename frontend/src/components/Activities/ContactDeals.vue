<template>
  <div>
    <DealsListView
      v-if="rows.length"
      class="mt-4"
      :rows="rows"
      :columns="columns"
      :options="{ selectable: false, showTooltip: false }"
    />
    <div
      v-if="!rows.length"
      class="grid flex-1 place-items-center text-xl font-medium text-gray-500 justify-center h-[100vh]"
    >
      <div class="flex flex-col items-center justify-center space-y-3">
      <DealEmpty class="h-[196px]  w-[196px] " />
        <span>{{ __('No {0} Found', [__('Deals')]) }}</span>
              <span class="text-gray-700 text-center font-inter text-sm font-normal leading-[20px]">{{'Your next big deal is out there - start tracking, negotiating, and closing like a pro!' }}</span>  

        
      </div>
    </div>
  </div>
</template>
<script setup>
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import DealsListView from '@/components/ListViews/DealsListView.vue'
import { organizationsStore } from '@/stores/organizations'
import { statusesStore } from '@/stores/statuses'
import { usersStore } from '@/stores/users'
import { dateFormat, dateTooltipFormat, formatNumberIntoCurrency, timeAgo } from '@/utils'
import { createResource } from 'qbs-vue-ui'
import { computed } from 'vue'
import DealEmpty from '@/components/Icons/DealEmpty.vue'

const { getUser } = usersStore()
const { getOrganization } = organizationsStore()
const { getDealStatus } = statusesStore()
const props = defineProps({
  tab: {
    type: Object,
    required: true,
  },
  contactId: {
    type: String,
    required: true,
  },
})

const rows = computed(() => {
  if (!deals.data || deals.data == []) return []

  return deals.data.map((row) => getDealRowObject(row))
})

const columns = computed(() => dealColumns)
const deals = createResource({
  url: 'crm.api.contact.get_linked_deals',
  cache: ['deals', props.contactId],
  params: {
    contact: props.contactId,
  },
  auto: true,
})
function getDealRowObject(deal) {
  return {
    name: deal.name,
    organization: {
      label: deal.organization,
      logo: getOrganization(deal.organization)?.organization_logo,
    },
    annual_revenue: formatNumberIntoCurrency(
      deal.annual_revenue,
      deal.currency,
    ),
    status: {
      label: deal.status,
      color: getDealStatus(deal.status)?.iconColorClass,
    },
    email: deal.email,
    mobile_no: deal.mobile_no,
    deal_owner: {
      label: deal.deal_owner && getUser(deal.deal_owner).full_name,
      ...(deal.deal_owner && getUser(deal.deal_owner)),
    },
    modified: {
      label: dateFormat(deal.modified, dateTooltipFormat),
      timeAgo: __(timeAgo(deal.modified)),
    },
  }
}
const dealColumns = [
  {
    label: __('Organization'),
    key: 'organization',
    width: '11rem',
  },
  {
    label: __('Amount'),
    key: 'annual_revenue',
    width: '9rem',
  },
  {
    label: __('Status'),
    key: 'status',
    width: '10rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Mobile no'),
    key: 'mobile_no',
    width: '11rem',
  },
  {
    label: __('Deal owner'),
    key: 'deal_owner',
    width: '10rem',
  },
  {
    label: __('Last modified'),
    key: 'modified',
    width: '8rem',
  },
]
</script>
