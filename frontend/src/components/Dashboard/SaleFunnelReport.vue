<template>
  <div
    class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full overflow-y-auto"
  >
    <h3 class="text-lg font-medium mb-4 text-gray-900">Sales Funnel Report</h3>
    <div v-if="salsFunnelUpdateKey.isLoading" class="flex justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <component :is="leadConversionUpdateKey.icon" class="!h-10 !w-10" />
        <div>{{ __('Loading data...') }}</div>
      </div>
    </div>
    <HorizondalBarGraph
      :key="salsFunnelUpdateKey.value"
      :chartData="salesFunnelData || []"
      v-else
    />
  </div>
</template>
<script setup>
import HorizondalBarGraph from '@/components/Dashboard/HorizondalBarGraph.vue'

import { ref } from 'vue'
const salesFunnelData = ref([])
const salsFunnelUpdateKey = ref({ key: 0, isLoading: false })
const API_BASE_PATH = `${window.location.origin}/api/method/`

const get_SalesFunnelReport = async () => {
  salsFunnelUpdateKey.value.isLoading = true
  try {
    const response = await fetch(
      `${API_BASE_PATH}crm.api.reports.get_funnel_data`,
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
      salesFunnelData.value = convertSalesFunnelData(data.message)
      salsFunnelUpdateKey.value.value = new Date().getTime()
    }
  } catch (error) {
    console.error('Failed to parse server error message:', parseError)
  } finally {
    salsFunnelUpdateKey.value.isLoading = false
  }
}
get_SalesFunnelReport()

function convertSalesFunnelData(message) {
  // Ensure message is an array before mapping
  const data = Array.isArray(message) ? message : []
  return data.map((item) => ({
    type: 'bar',
    showInLegend: true,
    name: item.FunnelStage, // Use DealStage as the name
    color: generateRandomColor(), // Optional: Generate a unique color for each DealStage
    dataPoints: [
      { y: item.TotalLeads || 0, label: 'Total Deals' }, // Replace undefined/null with 0
      { y: item.TotalDealValue || 0, label: 'Total Deal Value' },
      { y: item.PreviousStageLeads || 0, label: 'Previous Stage Leads' },
      { y: item.ConversionRate || 0, label: 'Conversion Rate' },
    ],
  }))
}

function generateRandomColor() {
  // Generate a random hue (0-360 degrees)
  const hue = Math.floor(Math.random() * 360)
  // High saturation (70-100%) and brightness (50-70%)
  const saturation = Math.floor(Math.random() * 31) + 70 // 70% to 100%
  const lightness = Math.floor(Math.random() * 21) + 50 // 50% to 70%

  // Convert HSL to a CSS-compatible string
  return `hsl(${hue}, ${saturation}%, ${lightness}%)`
}
</script>
