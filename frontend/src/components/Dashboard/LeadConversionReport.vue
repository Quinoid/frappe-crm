<template>
  <div
    class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full overflow-y-auto"
  >
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-medium mb-4 text-gray-900">
        Lead Conversion Report
      </h3>
      <div class="flex gap-1">
        <span @click="graphView = true" class="cursor-pointer">
          <GraphIcon
            class="h-4 w-4"
            :class="graphView ? 'text-green-600' : 'text-gray-600'"
          />
        </span>
        <span @click="graphView = false" class="cursor-pointer">
          <GridIcon
            class="h-4 w-4"
            :class="!graphView ? 'text-green-600' : 'text-gray-600'"
        /></span>
      </div>
    </div>
    <div v-if="leadConversionUpdateKey.isLoading" class="flex justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <component :is="leadConversionUpdateKey.icon" class="!h-10 !w-10" />
        <div>{{ __('Loading data...') }}</div>
      </div>
    </div>
    <div
      v-else-if="tableData?.length === 0"
      class="text-center text-gray-500 mt-4 p-3"
    >
      <div class="flex h-full items-center justify-center">
        <div
          class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
        >
          <GraphIcon class="h-10 w-10" />
          <span class="text-sm text-gray-500"> No Data Available</span>
        </div>
      </div>
    </div>
    <div v-else>
      <template v-if="graphView">
        <BarChart
          :key="leadConversionUpdateKey.value"
          :chartData="leadConversionReportData || []"
        />
      </template>
      <template v-else>
        <div class="data-table">
          <table
            class="table-auto border-collapse border border-gray-400 w-full text-left"
          >
            <thead>
              <tr class="bg-gray-100">
                <th class="border border-gray-300 px-4 py-2">Lead Source</th>
                <th class="border border-gray-300 px-4 py-2">
                  Converted Leads
                </th>
                <th class="border border-gray-300 px-4 py-2">
                  Avg Conversion Time
                </th>
                <th class="border border-gray-300 px-4 py-2">
                  Total Deal Value
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in tableData" :key="index">
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.LeadSource }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.ConvertedLeads }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.AvgConversionTime }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ formatCurrency(item.TotalDealValue) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  </div>
</template>
<script setup>
import BarChart from '@/components/Dashboard/BarChart.vue'
import GraphIcon from '@/components/GraphIcon.vue'
import GridIcon from '@/components/GridIcon.vue'
import { ref } from 'vue'
const leadConversionReportData = ref([])
const leadConversionUpdateKey = ref({ key: 0, isLoading: false })
const API_BASE_PATH = `${window.location.origin}/api/method/`
const graphView = ref(true)
const tableData = ref([])
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
      tableData.value = data.message
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
    backgroundColor: Array.from({ length: categories.length }, () =>
      generateRandomColor(),
    ),
    borderColor: Array.from({ length: categories.length }, () =>
      generateRandomColor(),
    ),
  }
  const datasets = categories.map((category,index) => ({
    label: category,
    data: inputData?.map((item) => item[category]),
    backgroundColor: colors.backgroundColor[index],
    borderColor: colors.borderColor[index],
    borderWidth: 2, // Border thickness
  }))

  return {
    labels: inputData?.map((item) => item.LeadSource),
    datasets: datasets,
  }
}
function formatCurrency(value) {
  return Number(value).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
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
