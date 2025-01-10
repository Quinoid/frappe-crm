
<template>
  <div>
    <div
      v-if="chartData.length"
      ref="chartContainer"
      style="width: 100%; height: 360px"
    ></div>
    <div v-else>
      <div class="flex flex-col items-center justify-center">
        <div class="text-gray-500 text-2xl">No data available</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted, computed } from 'vue'
import * as CanvasJS from '@canvasjs/charts'

export default {
  props: {
    chartData: {
      type: Array,
      required: true,
      default: () => [],
    },
  },
  setup(props) {
    const chartRef = ref(null)
    const chartContainer = ref(null)

    const validateChartData = (data) => {
      if (!Array.isArray(data)) return []
      return data.map((item) => ({
        ...item,
        dataPoints: Array.isArray(item.dataPoints)
          ? item.dataPoints.map((point) => ({
              label: point?.label || 'N/A',
              y: point?.y || 0,
            }))
          : [],
      }))
    }

    const chartOptions = computed(() => ({
      animationEnabled: true,
      theme: 'light2',
      axisY: {
        title: '',
        includeZero: true,
      },
      legend: {
        cursor: 'pointer',
        itemclick: toggleDataSeries,
      },
      toolTip: {
        shared: true,
        content: toolTipFormatter,
      },
      data: validateChartData(props.chartData),
    }))

    const toolTipFormatter = (e) => {
      if (!e.entries || !e.entries.length) return 'No data available'
      let content = ''
      for (const entry of e.entries) {
        content += `<span style="color:${entry.dataSeries.color}">${entry.dataSeries.name}</span>: <strong>${entry.dataPoint.y}</strong> <br/>`
      }
      return content
    }

    const toggleDataSeries = (e) => {
      if (typeof e.dataSeries.visible === 'undefined' || e.dataSeries.visible) {
        e.dataSeries.visible = false
      } else {
        e.dataSeries.visible = true
      }
      if (chartRef.value) {
        chartRef.value.render()
      }
    }

    onMounted(() => {
      if (chartContainer.value) {
        chartRef.value = new CanvasJS.Chart(
          chartContainer.value,
          chartOptions.value,
        )
        chartRef.value.render()
      }
    })

    watch(
      () => props.chartData,
      (newData) => {
        if (chartRef.value) {
          chartRef.value.options.data = validateChartData(newData)
          chartRef.value.render()
        }
      },
      { deep: true },
    )

    return {
      chartRef,
      chartContainer,
    }
  },
}
</script>
