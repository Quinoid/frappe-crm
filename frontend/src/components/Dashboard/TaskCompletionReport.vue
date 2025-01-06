<template>
  <div
    class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full overflow-y-auto"
  >
    <h3 class="text-lg font-medium mb-4 text-gray-900">
      Task Completion Report
    </h3>
    <div v-if="taskCompletionUpdateKey.isLoading" class="flex justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <component :is="leadConversionUpdateKey.icon" class="!h-10 !w-10" />
        <div>{{ __('Loading data...') }}</div>
      </div>
    </div>
    <BarChart
      v-else
      :chartData="taskCompletionReportData || []"
      :key="taskCompletionUpdateKey.value"
    />
  </div>
</template>
<script setup>
import BarChart from '@/components/Dashboard/BarChart.vue'

import { ref } from 'vue'
const taskCompletionReportData = ref([])
const taskCompletionUpdateKey = ref({ key: 0, isLoading: false })
const API_BASE_PATH = `${window.location.origin}/api/method/`

const getTaskCompletionData = async () => {
  taskCompletionUpdateKey.value.isLoading = true
  try {
    const response = await fetch(
      `${API_BASE_PATH}crm.api.reports.get_task_summary_data`,
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
      taskCompletionReportData.value = transformTaskData(data.message)
      taskCompletionUpdateKey.value.value = new Date().getTime()
    }
  } catch (error) {
    console.error('Failed to parse server error message:', parseError)
  } finally {
    taskCompletionUpdateKey.value.isLoading = false
  }
}
getTaskCompletionData()

function transformTaskData(inputData) {
  const categories = [
    'TotalTasks',
    'CompletedTasks',
    'OverdueTasks',
    'AvgCompletionTime',
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
    labels: inputData?.map((item) => item.AssignedTo),
    datasets: datasets,
  }
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
