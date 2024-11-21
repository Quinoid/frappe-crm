<template>
  <div class="communication-detail bg-white p-6 rounded-lg shadow-lg space-y-6">
    <!-- Header Section -->
    <div class="header border-b pb-4">
      <h2 class="text-xl font-semibold text-gray-800 mb-2">
        {{ message.subject }}
      </h2>
      <div class="details space-y-2">
        <p class="text-sm text-gray-600">
          <strong class="font-medium text-gray-700">From:</strong>
          {{ message.sender }}
        </p>
        <p class="text-sm text-gray-600">
          <strong class="font-medium text-gray-700">To:</strong>
          {{ message.recipients }}
        </p>
        <p v-if="message.cc" class="text-sm text-gray-600">
          <strong class="font-medium text-gray-700">CC:</strong>
          {{ message.cc }}
        </p>
        <p v-if="message.bcc" class="text-sm text-gray-600">
          <strong class="font-medium text-gray-700">BCC:</strong>
          {{ message.bcc }}
        </p>
      </div>
    </div>

    <!-- Content Section -->
    <div class="content">
      <div class="text-sm text-gray-700 leading-relaxed">
        <h3 class="font-medium text-lg text-gray-800 mb-4">Content:</h3>
        <div v-html="message.content" class="prose max-w-none"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createResource } from 'qbs-vue-ui'
const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
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
      actual_mobile_no: data.mobile_no,
      mobile_no: data.mobile_no,
    }
  },
})
</script>

<style>
/* Additional Tailwind utilities are used directly in the template */
</style>
