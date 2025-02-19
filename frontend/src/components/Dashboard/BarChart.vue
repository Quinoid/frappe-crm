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
<template v-if="chartData.labels.length > 0">
  <Bar class="h-full w-full" id="my-chart-id" :options="chartOptions" :data="chartData" />
</template>

<script>
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from 'chart.js';
import { defineComponent, toRefs } from 'vue';
import { Bar } from 'vue-chartjs';

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
    const chartOptions = {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
        },
        title: {
          display: false,
          text: 'Monthly Data Overview',
        },

      },
      scales: {
        x: {
          barPercentage: 0.5, // Adjust space between bars (0 to 1)
          categoryPercentage: 0.8, // Controls the width of bars relative to the category
        },
        y: {
          beginAtZero: true,
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
