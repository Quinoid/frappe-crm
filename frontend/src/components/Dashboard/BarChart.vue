<!-- <template>
  <Bar
    class="h-full w-full"
    id="my-chart-id"
    :options="chartOptions"
    :data="chartData"
  />
</template>

<script>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  name: 'BarChart',
  components: { Bar },

  data() {
    return {
      chartData: {
        labels: ['Campaign', 'Advertisement'],
        datasets: [
          {
            label: 'TotalDeals',
            data: [1212, 1212],
            backgroundColor: ['#3498db'], // Colors for the bars
            borderColor: ['#2980b9'], // Border colors
            borderWidth: 2, // Border thickness
          },
          {
            label: 'TotalDealValue',
            data: [709372122, 500000],
            backgroundColor: ['#3498db'], // Colors for the bars
            borderColor: ['#2980b9'], // Border colors
            borderWidth: 2, // Border thickness
          },
          {
            label: 'WeightedDealValue',
            data: [660155933.4, 125000],
            backgroundColor: ['#3498db'], // Colors for the bars
            borderColor: ['#2980b9'], // Border colors
            borderWidth: 2, // Border thickness
          },
          {
            label: 'AvgCloseProbability',
            data: [111111.1111, 22111],
            backgroundColor: ['#3498db'], // Colors for the bars
            borderColor: ['#2980b9'], // Border colors
            borderWidth: 2, // Border thickness
          },
        ],
      },
      chartOptions: {
        responsive: true,
        plugins: {
          legend: {
            display: true,
            position: 'top',
          },
          title: {
            display: true,
            text: 'Monthly Data Overview',
          },
        },
      },
    }
  },
}
</script> -->
<template>
  <Bar
    class="h-full w-full"
    id="my-chart-id"
    :options="chartOptions"
    :data="chartData"
    v-if="chartData.datasets.length > 0"
  />
  <div v-else>
    <div class="flex flex-col items-center justify-center">
      <div class="text-gray-500 text-2xl">No data available</div>
    </div>
  </div>
</template>

<script>
import { defineComponent, toRefs } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default defineComponent({
  name: 'BarChart',
  components: { Bar },
  props: {
    chartData: {
      type: Object,
      required: true,
      default: () => ({
        labels: [],
        datasets: [
          {
            label: '',
            data: [],
          },
        ],
      }),
    },
  },
  setup(props) {
    // Destructure props for reactivity
    const { chartData } = toRefs(props)
    console.log(chartData.value, 'chartData')
    const chartOptions = {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          position: 'top',
        },
        title: {
          display: true,
          text: 'Monthly Data Overview',
        },
      },
    }

    return {
      chartData,
      chartOptions,
    }
  },
})
</script>
