<template>
  <div
    class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full overflow-y-auto"
  >
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-medium mb-4 text-gray-900">
        Team Performance Report
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

    <div v-if="teamPerformanceUpdateKey.isLoading" class="flex justify-center">
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
          :chartData="teamPerformanceReportData || []"
          :key="teamPerformanceUpdateKey.value"
        />
      </template>
      <template v-else>
        <div class="data-table">
          <table
            class="table-auto border-collapse border border-gray-400 w-full text-left"
          >
            <thead>
              <tr class="bg-gray-100">
                <th class="border border-gray-300 px-4 py-2">User Name</th>
                <th class="border border-gray-300 px-4 py-2">Total Tasks</th>
                <th class="border border-gray-300 px-4 py-2">
                  Completed Tasks
                </th>
                <th class="border border-gray-300 px-4 py-2">Total Deals</th>
                <th class="border border-gray-300 px-4 py-2">
                  Total Deal Value
                </th>
                <th class="border border-gray-300 px-4 py-2">
                  Total Emails Sent
                </th>
                <th class="border border-gray-300 px-4 py-2">Total Calls</th>
                <th class="border border-gray-300 px-4 py-2">Total Meetings</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in tableData" :key="index">
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.UserName }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.TotalTasks }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.CompletedTasks }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.TotalDeals }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ formatCurrency(item.TotalDealValue) }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.TotalEmailsSent }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.TotalCalls }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.TotalMeetings }}
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
const teamPerformanceReportData = ref([])
const teamPerformanceUpdateKey = ref({ key: 0, isLoading: false })
const API_BASE_PATH = `${window.location.origin}/api/method/`
const graphView = ref(true)
const tableData = ref([])
const get_teamPerformanceReport = async () => {
  teamPerformanceUpdateKey.value.isLoading = true
  try {
    const response = await fetch(
      `${API_BASE_PATH}crm.api.reports.get_user_summary`,
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
      tableData.value = data.message?.summary
      teamPerformanceReportData.value = transformteamPerformanceReport(
        data.message?.summary,
      )
      teamPerformanceUpdateKey.value.value = new Date().getTime()
    }
  } catch (error) {
    console.error('Failed to parse server error message:', parseError)
  } finally {
    teamPerformanceUpdateKey.value.isLoading = false
  }
}
get_teamPerformanceReport()

function transformteamPerformanceReport(inputData) {
  const categories = [
    'TotalTasks',
    'CompletedTasks',
    'TotalDeals',
    'TotalDealValue',
    'TotalEmailsSent',
    'TotalCalls',
    'TotalMeetings',
  ]
  const colors = {
    backgroundColor: Array.from({ length: categories.length }, () =>
      generateRandomColor(),
    ),
    borderColor: Array.from({ length: categories.length }, () =>
      generateRandomColor(),
    ),
  }
  const datasets = categories.map((category) => ({
    label: category,
    data: inputData.map((item) => item[category]),
    backgroundColor: colors.backgroundColor[index],
    borderColor: colors.borderColor[index],
    borderWidth: 2, // Border thickness
  }))
  return {
    labels: inputData?.map((item) => item.UserName),
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
