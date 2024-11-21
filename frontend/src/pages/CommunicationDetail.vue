<template>
  <LayoutHeader v-if="message.data">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
  </LayoutHeader>
  <div v-if="message?.data" class="w-full p-8">
    <div
      class="communication-detail bg-white p-6 rounded-sm shadow-sm space-y-6"
    >
      <!-- Header Section -->
      <div class="header border-b pb-4">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">
          {{ message.data.subject }}
        </h2>
        <div class="details space-y-2 flex flex-col gap-2.5">
          <p class="text-sm text-gray-600">
            <strong class="font-medium text-gray-700">From:</strong>
            {{ message.data.sender }}
          </p>
          <p class="text-sm text-gray-600">
            <strong class="font-medium text-gray-700">To:</strong>
            {{ message.data.recipients }}
          </p>
          <p v-if="message.data.cc" class="text-sm text-gray-600">
            <strong class="font-medium text-gray-700">CC:</strong>
            {{ message.data.cc }}
          </p>
          <p v-if="message.data.bcc" class="text-sm text-gray-600">
            <strong class="font-medium text-gray-700">BCC:</strong>
            {{ message.data.bcc }}
          </p>
        </div>
      </div>

      <!-- Content Section -->
      <div class="content">
        <div class="text-sm text-gray-700 leading-relaxed">
          <h3 class="font-medium text-lg text-gray-800 mb-4">Content:</h3>
          <div v-html="message.data.content" class="prose max-w-none"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createResource, Breadcrumbs } from 'qbs-vue-ui'
import { computed } from 'vue'
import { getView } from '@/utils/view'
import { useRoute } from 'vue-router'

import LayoutHeader from '@/components/LayoutHeader.vue'
import Icon from '@/components/Icon.vue'
const props = defineProps({
  communicationId: {
    type: String,
    required: true,
  },
})
const route = useRoute()
const breadcrumbs = computed(() => {
  let items = [{ label: __('Communication'), route: { name: 'Communication' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(
      route.query.view,
      route.query.viewType,
      'CommunicationDetail',
    )
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Communication',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: message.data?.sender,
    route: {
      name: 'CommunicationDetail',
      params: { communicationId: props.communicationId },
    },
  })
  return items
})
const message = createResource({
  url: 'crm.api.communication.custom_get_communication_details',
  cache: ['Communication', props.communicationId],
  params: {
    name: props.communicationId,
  },
  auto: true,
  transform: (data) => {
    return {
      ...data,
    }
  },
})
</script>

<style>
/* Additional Tailwind utilities are used directly in the template */
</style>
