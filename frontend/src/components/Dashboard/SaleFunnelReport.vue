<template>
  <div
    class="bg-white shadow-sm grid lg:col-span-3 col-span-6  rounded-lg p-6 sm:w-full w-full overflow-y-auto"
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
        class="!w-[230px]"
        :disabled="false"
      />
            <ToolTipInfo />

     </div>
      <div class="flex gap-2 graph-actions ">
          
        <span @click="graphView = true" class="cursor-pointer" :class="graphView ? 'bg-white' : ''">
          <Tooltip :text="__('Graph View')">
          <GraphIcon
            class="h-6 w-6"
            :class="'text-icon_color'"
          />
          </Tooltip>
        </span>
        <span @click="graphView = false" class="cursor-pointer p-[2px]" :class="!graphView ? 'bg-white' : ''">
          <Tooltip :text="__('Grid View')">
          <GridIcon
            class="h-6 w-6"
            :class="'text-icon_color'"
        />
              </Tooltip>
        </span>

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
      <div class="flex h-full items-center justify-center min-h-[260px]">
        <div
          class="flex flex-col relative justify-center items-center gap-3 text-xl font-medium text-gray-500"
        >
          <EmptyFunnel />
          <span class="nodata-text"> Not enough data to display visualization.</span>
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
                <th class="border border-gray-300 px-4 py-2 text-right">Total Leads / Deals </th>
                <th class="border border-gray-300 px-4 py-2 text-right">
                  Total Deal Value
                </th>
                <th class="border border-gray-300 px-4 py-2 text-right">
                  Previous Stage Leads
                </th>
                <th class="border border-gray-300 px-4 py-2 text-right">Drop-off Rate (%)</th>
                <th class="border border-gray-300 px-4 py-2 text-right">
                  Conversion Rate (%)
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in tableData" :key="index">
                <td class="border border-gray-300 px-4 py-2">
                  {{ item.FunnelStage }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-right">
                  {{ item.TotalLeads }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-right">
                  {{ formatCurrency(item.TotalDealValue) }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-right">
                  {{ item.PreviousStageLeads }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-right">{{ item.DropOffRate }}</td>
                <td class="border border-gray-300 px-4 py-2 text-right">
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
import HorizondalBarGraph from '@/components/Dashboard/HorizondalBarGraph.vue';
import ToolTipInfo from '@/components/Dashboard/TootlTipInfo.vue';
import GraphIcon from '@/components/GraphIcon.vue';
import GridIcon from '@/components/GridIcon.vue';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { DateRangePicker, Tooltip } from 'qbs-vue-ui';
import { ref, watch } from 'vue';
import { formatDate, revertDate } from '../../utils/index';
import EmptyFunnel from '@/components/Dashboard/EmptyFunnel.vue'
const salesFunnelData = ref([])
const salsFunnelUpdateKey = ref({ key: 0, isLoading: false })
const API_BASE_PATH = `${window.location.origin}/api/method/`
const graphView = ref(true)
const tableData = ref([])
const dateRange = ref([formatDate(new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0]), formatDate(new Date().toISOString().split('T')[0])])
const filterData = ref(dateRange.value.join(' to '));
const get_SalesFunnelReport = async () => {
  
  salsFunnelUpdateKey.value.isLoading = true
  const filters=filterData.value.split(' to ')
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
      salesFunnelData.value = convertToFunnelData(data.message)
      salsFunnelUpdateKey.value.value = new Date().getTime()
    }
  } catch (error) {
    console.error('Failed to parse server error message:', error)
  } finally {
    salsFunnelUpdateKey.value.isLoading = false
  }
}
get_SalesFunnelReport()


function convertToFunnelData(inputData) {
    const sortedData = inputData.sort((a, b) => b.TotalLeads - a.TotalLeads);
  const colorsObj = {
    "New": "#DB5C4F",
    "Engaged": "#8C52C1",
    "Qualified": "#34C5B7",
    "Ongoing": "#8C52C1",
    "Negotiation": "#0077B5",
    "Closed Won": "#E7BD88"
  }
  return [
    {
      type: "funnel",
      yValueFormatString: "#,###\"\"",
      indexLabel: "{label} - {y}",
      neckHeight: 0,
      dataPoints: sortedData.map(item => ({
        y: item.TotalLeads,
        label: item.FunnelStage,
        color: colorsObj[item.FunnelStage],
      }))
    }
  ];
}
watch(
  () => filterData.value, // Watching the entire array
  (newVal, oldVal) => {
    const filters = newVal.split(',');
    if (filters.length === 2) {
 const newData = [formatDate(filters[0]), formatDate(filters[1])]
      filterData.value = newData.join(' to ');
    }

    get_SalesFunnelReport(); // Call the API whenever the object changes
  },
  { deep: true } // Ensure nested changes are detected
);
  function exportToPDF() {
      const doc = new jsPDF();
      const columns = ['Funnel Stage', 'Total Leads / Deals ', 'Total Deal Value', 'Previous Stage Leads', 'Drop-off Rate (in %)', 'Conversion Rate (in %)'];
      const rows = tableData.value.map((user) => [user.FunnelStage, user.TotalLeads, user.TotalDealValue, user.PreviousStageLeads,user.DropOffRate, user.ConversionRate]);

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
