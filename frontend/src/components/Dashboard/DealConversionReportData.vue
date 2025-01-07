<template>
  <div
    class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full overflow-y-auto"
  >
   
    <div class="flex justify-between items-center mb-4 ">
      <div class="flex gap-2 items-center">
      <h3 class="text-lg font-medium  text-gray-900">
        Deal Pipeline Report
      </h3>
      <DateRangePicker
        v-model="filterData"
        variant="subtle"
        class="!w-[210px]"
        placeholder="Placeholder"
        :disabled="false"
      />
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
    <div v-if="dealSummaryUpdateKey.isLoading" class="flex justify-center">
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
        <HorizondalBarGraph
          :chartData="dealSummaryReportData || []"
          :key="dealSummaryUpdateKey.value"
        />
      </template>
      <template v-else>
        <div class="data-table overflow-auto table-container">
          <table
            class="table-auto border-collapse border border-gray-400 w-full text-left"
          >
            <thead>
              <tr class="bg-gray-100">
                <th class="border border-gray-300 px-4 py-2">Deal Stage</th>
                <th class="border border-gray-300 px-4 py-2">Total Deals</th>
                <th class="border border-gray-300 px-4 py-2">
                  Total Deal Value
                </th>
                <th class="border border-gray-300 px-4 py-2">
                  Weighted Deal Value
                </th>
                <th class="border border-gray-300 px-4 py-2">
                  Avg Close Probability (%)
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in tableData" :key="index">
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.DealStage }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.TotalDeals }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ formatCurrency(item.TotalDealValue) }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ formatCurrency(item.WeightedDealValue) }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.AvgCloseProbability }}
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
import HorizondalBarGraph from '@/components/Dashboard/HorizondalBarGraph.vue'
import { ref ,watch} from 'vue'
import GraphIcon from '@/components/GraphIcon.vue'
import GridIcon from '@/components/GridIcon.vue'
import { Tooltip,DateRangePicker } from 'qbs-vue-ui'
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { generateRandomColor } from '@/utils/colors'
const dealSummaryReportData = ref([])
const dealSummaryUpdateKey = ref({ key: 0, isLoading: false })
const API_BASE_PATH = `${window.location.origin}/api/method/`
const graphView = ref(true)
const tableData = ref([])
const dateRange = ref([new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],new Date().toISOString().split('T')[0]])
const filterData = ref(dateRange.value.join(','));
const get_dealSummaryData = async () => {
    const filters=filterData.value.split(',')

  dealSummaryUpdateKey.value.isLoading = true
  try {
    const response = await fetch(
      `${API_BASE_PATH}crm.api.reports.get_deal_summary_data`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token,
        },
        body: JSON.stringify({
           start_date: filters[0],
          end_date: filters[1],
        }),
      },
    )

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData._server_messages || response.statusText)
    } else {
      const data = await response.json()
      dealSummaryReportData.value = convertToChartData(data.message)
      tableData.value = data.message
      console.log(tableData.value, data.message)
      dealSummaryUpdateKey.value.value = new Date().getTime()
    }
  } catch (error) {
    console.error('Failed to parse server error message:', parseError)
  } finally {
    dealSummaryUpdateKey.value.isLoading = false
  }
}
get_dealSummaryData()
watch(
  () => filterData.value, // Watching the entire array
  (newVal, oldVal) => {

    get_dealSummaryData(); // Call the API whenever the object changes
  },
  { deep: true } // Ensure nested changes are detected
);
function convertToChartData(message) {
  return message.map((item) => ({
    type: 'bar',
    showInLegend: true,
    name: item.DealStage, // Use DealStage as the name
    color: generateRandomColor(), // Optional: Generate a unique color for each DealStage
    dataPoints: [
      { y: item.TotalDeals, label: 'Total Deals' },
      { y: item.TotalDealValue, label: 'Total Deal Value' },
      { y: item.WeightedDealValue, label: 'Weighted Deal Value' },
      { y: item.AvgCloseProbability, label: 'Avg Close Probability' },
    ],
  }))
}

 function exportToPDF() {
      const doc = new jsPDF();
      const columns = ['Deal Stage', 'Total Deals', 'Total Deal Value', 'Weighted Deal Value', 'Avg Close Probability'];
      const rows = tableData.value.map((user) => [user.DealStage, user.TotalDeals, user.TotalDealValue, user.WeightedDealValue, user.AvgCloseProbability]);

      doc.text('Deal Pipeline Report', 14, 10);
      autoTable(doc, {
        head: [columns],
        body: rows,
      });
      const date=new Date();
      const filename = "deal-pipeline-report-" + date.getFullYear() + "-" + (date.getMonth()+1) + "-" + date.getDate() + ".pdf";
      doc.save(filename);
    }
  
function formatCurrency(value) {
  return Number(value).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
</script>
