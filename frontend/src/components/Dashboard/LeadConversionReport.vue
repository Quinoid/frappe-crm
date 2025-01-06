<template>
  <div
    class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full overflow-y-auto"
  >
    <h3 class="text-lg font-medium mb-4 text-gray-900">
      Lead Conversion Report
    </h3>
    <div v-if="leadConversionUpdateKey.isLoading" class="flex justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <component :is="leadConversionUpdateKey.icon" class="!h-10 !w-10" />
        <div>{{ __('Loading data...') }}</div>
      </div>
    </div>
    <BarChart
      :key="leadConversionUpdateKey.value"
      :chartData="leadConversionReportData || []"
    />
  </div>
</template>
<script setup>
import BarChart from '@/components/Dashboard/BarChart.vue'

import { ref } from 'vue'
const leadConversionReportData = ref([])
const leadConversionUpdateKey = ref({ key: 0, isLoading: false })
const API_BASE_PATH = `${window.location.origin}/api/method/`

const get_LeadConversionData = async () => {
  leadConversionUpdateKey.value.isLoading = true
  try {
    const response = await fetch(
      `${API_BASE_PATH}crm.api.reports.get_lead_conversion_data`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token,
        },
        body: JSON.stringify({
          start_date: '2023-01-01',
          end_date: '2026-01-31',
        }),
      },
    )

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData._server_messages || response.statusText)
    } else {
        const data = await response.json()
      leadConversionReportData.value = transformLeadData(data.message)
      leadConversionUpdateKey.value.value = new Date().getTime()
    }
  } catch (error) {
    console.error('Failed to parse server error message:', parseError)
  } finally {
    leadConversionUpdateKey.value.isLoading = false
  }
}
get_LeadConversionData()

function transformLeadData(inputData) {
  const categories = ['ConvertedLeads', 'AvgConversionTime', 'TotalDealValue']
  const colors = {
    backgroundColor: ['#3498db'], // Colors for the bars
    borderColor: ['#2980b9'], // Border colors
  }
  const datasets = categories.map((category) => ({
    label: category,
    data: inputData?.map((item) => item[category]),
    backgroundColor: colors.backgroundColor,
    borderColor: colors.borderColor,
    borderWidth: 2, // Border thickness
  }))

  return {
    labels: inputData?.map((item) => item.LeadSource),
    datasets: datasets,
  }
}
</script>
