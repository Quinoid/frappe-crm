<!-- <script>
import { ref, onMounted, computed, watch, nextTick, toRaw } from 'vue'
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
    const chartOptions = computed(() => ({
      animationEnabled: true,
      theme: 'light2',
      axisY: {
        title: 'Users',
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
      data: props.chartData,
    }))

    const chartRef = ref(null)
    const styleOptions = ref({
      width: '100%',
      height: '360px',
    })

    onMounted(() => {
      if (chartRef.value && chartRef.value.render) {
        chartRef.value.render()
      }
    })

    watch(
      () => props.chartData,
      async (newData) => {
        console.log('Updated chart data:', toRaw(newData)) // Use `toRaw` to log the plain object
        chartOptions.value.data = toRaw(newData)
        await nextTick()
        if (chartRef.value && chartRef.value.render) {
          console.log('Re-rendering chart...')
          chartRef.value.render()
        }
      },
      { deep: true }, // Add deep: true for array or object reactivity
    )
    function toolTipFormatter(e) {
      let content = ''
      if (e.entries.length > 1) {
        const percentageDifference =
          (e.entries[0].dataPoint.y - e.entries[1].dataPoint.y) /
          e.entries[1].dataPoint.y
        content += `<strong>${e.entries[0].dataPoint.label}</strong>`
        content += ` (<span style="color: ${
          percentageDifference >= 0 ? 'green' : 'red'
        }"> ${percentageDifference >= 0 ? '↑' : '↓'} ${CanvasJS.formatNumber(
          Math.abs(percentageDifference),
          '#0.##%',
        )}</span>)<br/>`
      }

      for (const entry of e.entries) {
        content += `<span style="color:${entry.dataSeries.color}">${entry.dataSeries.name}</span>: <strong>${entry.dataPoint.y}</strong> <br/>`
      }
      return content
    }

    // Toggle Data Series Visibility
    function toggleDataSeries(e) {
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
      console.log(chartOptions.value, 'horizondalBarGraph')
    })

    return {
      chartOptions,
      chartRef,
      styleOptions,
    }
  },
}
</script>

<template v-if="chartData.length">
  <CanvasJSChart
    ref="chartRef"
    v-if="chartData.length"
    :options="chartOptions"
    :styles="styleOptions"
  />
</template> -->
<template>
  <div>
    <div
      v-if="chartData.length"
      ref="chartContainer"
      style="width: 100%; height: 360px"
    ></div>
    <div v-else>No data available</div>
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
        title: 'Users',
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
