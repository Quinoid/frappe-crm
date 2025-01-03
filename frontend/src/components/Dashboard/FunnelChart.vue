<script>
  export default {
    data() {
      return {
        chart: null,
        options: {
          theme: "light2",
          animationEnabled: true,
          title: {
            text: "Sales Lifecycle"
          },
          data: [{
            type: "funnel",
            indexLabel: "{name}: {y}",
            valueRepresents: "area",
            dataPoints: [
              { y: 10000, name: "Prospect" },
              { y: 8200, name: "Qualified" },
              { y: 2500, name: "Price Quote" },
              { y: 1200, name: "Negotiation" },
              { y: 480, name: "Won" }
            ]
          }],
          copyright: {
            enabled: false // Disable the watermark
          }
        },
        styleOptions: {
          width: "100%",
          height: "360px"
        }
      }
    }
  }
</script>

<template>
  <CanvasJSChart :options="options" :style="styleOptions" />
</template>
