<template>
  <div
    class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full overflow-y-auto"
  >
  
        <div class="flex justify-between items-center mb-4 ">
      <div class="flex gap-2 items-center">
      <h3 class="text-lg font-medium  text-gray-900">
        Task Completion Report
      </h3>
      <DateRangePicker
        v-model="filterData"
        variant="subtle"
        placeholder="Placeholder"
        class="!w-[230px]"
        :disabled="false"
     />
           <ToolTipInfo />

    </div>
      <div class="flex gap-2">
        <Tooltip :text="__('Graph View')">
        <span @click="graphView = true" class="cursor-pointer">
          <GraphIcon
            class="h-4 w-4"
            :class="graphView ? 'text-green-600' : 'text-gray-600'"
          />
        </span>
        </Tooltip>
        <Tooltip :text="__('Grid View')">
        <span @click="graphView = false" class="cursor-pointer">
          <GridIcon
            class="h-4 w-4"
            :class="!graphView ? 'text-green-600' : 'text-gray-600'"
        /></span>
        </Tooltip>
        <Tooltip :text="__('Download PDF')">
          <a
            class="cursor-pointer hover:text-green-600"
            @click="exportToPDF()"
            target="_blank"
          >
            <FeatherIcon name="download" class="h-4 w-4" />
          </a>
        </Tooltip>
      </div>
    </div>
    <div v-if="taskCompletionUpdateKey.isLoading" class="flex justify-center">
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
          <span class="text-sm text-gray-500"> No  Data Available</span>
        </div>
      </div>
    </div>
    <div v-else>
      <template v-if="graphView">
        <BarChart
          :chartData="taskCompletionReportData || []"
          :key="taskCompletionUpdateKey.value"
        />
      </template>
      <template v-else>
        <div class="data-table overflow-auto table-container">
          <table
            class="table-auto border-collapse border border-gray-400 w-full text-left"
          >
            <thead>
              <tr class="bg-gray-100">
                <th class="border border-gray-300 px-4 py-2">Assigned To</th>
                <th class="border border-gray-300 px-4 py-2 text-right">Total Tasks</th>
                <th class="border border-gray-300 px-4 py-2 text-right">
                  Completed Tasks
                </th>
                <th class="border border-gray-300 px-4 py-2 text-right">Overdue Tasks</th>
                <th class="border border-gray-300 px-4 py-2 text-right">
                  Avg Completion Time (Days)
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in tableData" :key="index">
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.AssignedTo }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-right">
                  {{ item.TotalTasks }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-right">
                  {{ item.CompletedTasks }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-right" >
                  {{ item.OverdueTasks }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-right">
                  {{ item.AvgCompletionTime }}
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
import ToolTipInfo from '@/components/Dashboard/TootlTipInfo.vue'
import GraphIcon from '@/components/GraphIcon.vue'
import GridIcon from '@/components/GridIcon.vue'
import { generateRandomColor } from '@/utils/colors'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import { DateRangePicker, Tooltip } from 'qbs-vue-ui'
import { formatDate, revertDate } from '../../utils/index';

import { ref, watch } from 'vue'
const taskCompletionReportData = ref([])
const taskCompletionUpdateKey = ref({ key: 0, isLoading: false })
const API_BASE_PATH = `${window.location.origin}/api/method/`
const graphView = ref(true)
const tableData = ref([])
const dateRange = ref([formatDate(new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0]), formatDate(new Date().toISOString().split('T')[0])])
const filterData = ref(dateRange.value.join(' to '));
const getTaskCompletionData = async () => {
  const filters=filterData.value.split(' to ')

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
         start_date: revertDate(filters[0]),
          end_date: revertDate(filters[1]),
        }),
      },
    )

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData._server_messages || response.statusText)
    } else {
      const data = await response.json()
      tableData.value = data.message
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
watch(
  () => filterData.value, // Watching the entire array
  (newVal, oldVal) => {
  const filters = newVal.split(',');
    if (filters.length === 2) {
  const newData = [formatDate(filters[0]), formatDate(filters[1])]
      filterData.value = newData.join(' to ');
    }
    getTaskCompletionData(); // Call the API whenever the object changes
  },
  { deep: true } // Ensure nested changes are detected
);
const formatCamelCase = (str) => {
  return str.replace(/([a-z])([A-Z])/g, '$1 $2');
};

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

  const datasets = categories.map((category,index) => ({
    label: formatCamelCase(category),
    data: inputData.map((item) => item[category]),
    backgroundColor: colors.backgroundColor[index],
    borderColor: ['#ffffff'],
    borderWidth: 2, // Border thickness
  }))
  return {
    labels: inputData?.map((item) => item.AssignedTo),
    datasets: datasets,
  }
}
 function exportToPDF() {
      const doc = new jsPDF();
      const columns = ['Assigned To', 'Total Tasks', 'Completed Tasks', 'Overdue Tasks', 'Avg Completion Time (Days)'];
      const rows = tableData.value.map((user) => [user.AssignedTo, user.TotalTasks, user.CompletedTasks, user.OverdueTasks, user.AvgCompletionTime]);

      doc.text('Task Completion Report', 14, 10);
      autoTable(doc, {
        head: [columns],
        body: rows,
      });
      const date=new Date();
      const filename = "task-completion-report-" + date.getFullYear() + "-" + (date.getMonth()+1) + "-" + date.getDate() + ".pdf";
      doc.save(filename);
    } 

</script>
