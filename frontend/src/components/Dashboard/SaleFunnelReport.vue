<template>
  <div
    class="bg-white shadow-md rounded-lg p-6 sm:w-full w-full overflow-y-auto"
  >
    <div class="flex justify-between items-center mb-4 ">
      <div class="flex gap-2 items-center">
      <h3 class="text-lg font-medium  text-gray-900">
        Sales Funnel Report
      </h3>
      <DateRangePicker
        v-model="filterData"
        variant="subtle"
        placeholder="Placeholder"
        class="!w-[210px]"
        :disabled="false"
      />
     </div>
      <div class="flex gap-2 ">
          
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
    <div v-if="salsFunnelUpdateKey.isLoading" class="flex justify-center">
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
        <HorizondalBarGraph
          :key="salsFunnelUpdateKey.value"
          :chartData="salesFunnelData || []"
        />
      </template>
      <template v-else>
        <div class="data-table overflow-auto table-container">
          <table
            class="table-auto border-collapse border border-gray-400 w-full text-left"
          >   
            <thead>
              <tr class="bg-gray-100">
                <th class="border border-gray-300 px-4 py-2">Funnel Stage</th>
                <th class="border border-gray-300 px-4 py-2">Total Leads</th>
                <th class="border border-gray-300 px-4 py-2">
                  Total Deal Value
                </th>
                <th class="border border-gray-300 px-4 py-2">
                  Previous Stage Leads
                </th>
                <th class="border border-gray-300 px-4 py-2">
                  Conversion Rate
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in tableData" :key="index">
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.FunnelStage }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.TotalLeads }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ formatCurrency(item.TotalDealValue) }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.PreviousStageLeads }}
                </td>
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.ConversionRate }}
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
import GraphIcon from '@/components/GraphIcon.vue'
import GridIcon from '@/components/GridIcon.vue'
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { Tooltip ,DateRangePicker} from 'qbs-vue-ui'
import { ref ,watch } from 'vue'
import { generateRandomColor } from '@/utils/colors'
const salesFunnelData = ref([])
const salsFunnelUpdateKey = ref({ key: 0, isLoading: false })
const API_BASE_PATH = `${window.location.origin}/api/method/`
const graphView = ref(true)
const tableData = ref([])
const dateRange = ref([new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],new Date().toISOString().split('T')[0]])
const filterData = ref(dateRange.value.join(','));
const get_SalesFunnelReport = async () => {
  
  salsFunnelUpdateKey.value.isLoading = true
  const filters=filterData.value.split(',')
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
      tableData.value = data.message
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
watch(
  () => filterData.value, // Watching the entire array
  (newVal, oldVal) => {
    console.log(newVal,oldVal)

    get_SalesFunnelReport(); // Call the API whenever the object changes
  },
  { deep: true } // Ensure nested changes are detected
);
  function exportToPDF() {
      const doc = new jsPDF();
      const columns = ['Funnel Stage', 'Total Leads', 'Total Deal Value', 'Previous Stage Leads', 'Conversion Rate'];
      const rows = tableData.value.map((user) => [user.FunnelStage, user.TotalLeads, user.TotalDealValue, user.PreviousStageLeads, user.ConversionRate]);

      doc.text('Sales Funnel Report', 14, 10);
      autoTable(doc, {
        head: [columns],
        body: rows,
      });
      const date=new Date();
      const filename = "sales-funnel-report-" + date.getFullYear() + "-" + (date.getMonth()+1) + "-" + date.getDate() + ".pdf";
      doc.save(filename);
    }
  
function formatCurrency(value) {
  return Number(value).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

</script>
