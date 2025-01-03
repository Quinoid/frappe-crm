<template>
  <Line
    id="my-chart-id"
    class="h-full w-full"
    :options="chartOptions"
    :data="chartData"
  />
</template>

<script>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale
)

export default {
  name: 'LineChart',
  components: { Line },
  
  data() {
    return {
      chartData: {
        labels: ['Campaign', 'Advertisement'], // X-axis labels
        datasets: [
          {
            label: 'TotalDeals',
            data: [1212, 1212],
            backgroundColor: 'rgba(52, 152, 219, 0.5)', // Semi-transparent for points
            borderColor: '#3498db', // Line color
            fill: false, // No area fill
            tension: 0.4, // Smooth curves
          },
          {
            label: 'TotalDealValue',
            data: [709372122, 500000],
            backgroundColor: 'rgba(46, 204, 113, 0.5)',
            borderColor: '#2ecc71',
            fill: false,
            tension: 0.4,
          },
          {
            label: 'WeightedDealValue',
            data: [660155933.4, 125000],
            backgroundColor: 'rgba(231, 76, 60, 0.5)',
            borderColor: '#e74c3c',
            fill: false,
            tension: 0.4,
          },
          {
            label: 'AvgCloseProbability',
            data: [55, 25],
            backgroundColor: 'rgba(241, 196, 15, 0.5)',
            borderColor: '#f1c40f',
            fill: false,
            tension: 0.4,
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
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Values',
            },
          },
          x: {
            title: {
              display: true,
              text: 'Deal Stage',
            },
          },
        },
      },
    }
  },
}
</script>
