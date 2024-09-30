<template>
  <Popover
    :placement="isMobile ? 'bottom-start' : 'right-start'"
    class="flex w-full"
  >
    <template #target="{ togglePopover }">
      <button
        :class="[
          active ? 'bg-gray-100' : 'text-gray-800',
          'group w-full flex h-7 items-center justify-between rounded px-2 text-base hover:bg-gray-100',
        ]"
        @click.prevent="togglePopover()"
      >
        <div class="flex gap-2">
          <AppsIcon class="size-4" />
          <span class="whitespace-nowrap">
            {{ __('Apps') }}
          </span>
        </div>
        <FeatherIcon name="chevron-right" class="size-4 text-gray-600" />
      </button>
    </template>
    <template #body>
      <div
        class="grid grid-cols-3 justify-between mx-3 p-2 rounded-lg border border-gray-100 bg-white shadow-xl"
        :class="{ 'absolute top-0 left-0 w-full ml-0': isMobile }"
        @click.stop
      >
        <div v-for="app in apps.data" :key="app.name">
          <a
            :href="app.route"
            class="flex flex-col gap-1.5 rounded justify-center items-center py-2 px-1 hover:bg-gray-100"
            @click.stop="handleClick(app)"
            @touchstart.prevent="handleClick(app)"
          >
            <img class="size-8" :src="app.logo" />
            <div class="text-sm text-gray-700">
              {{ app.title }}
            </div>
          </a>
        </div>
      </div>
    </template>
  </Popover>
</template>
<script setup>
import AppsIcon from '@/components/Icons/AppsIcon.vue'
import { Popover, createResource } from 'qbs-vue-ui'
import { stopRecording } from '@/telemetry'
import { onUnmounted, onMounted, ref } from 'vue'

const props = defineProps({
  active: Boolean,
})

const apps = createResource({
  url: 'frappe.apps.get_apps',
  cache: 'apps',
  auto: true,
  transform: (data) => {
    let _apps = [
      {
        name: 'frappe',
        logo: '/assets/frappe/images/framework.png',
        title: __('Desk'),
        route: '/app',
      },
    ]
    data.map((app) => {
      if (app.name === 'crm') return
      _apps.push({
        name: app.name,
        logo: app.logo,
        title: __(app.title),
        route: app.route,
      })
    })

    return _apps
  },
})
function handleClick(app) {
  if (app.onClick) {
    app.onClick()
  } else {
    window.location.href = app.route // Fallback to navigation if no onClick
  }
}

const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  stopRecording()
})
</script>
<style scoped>
@media (max-width: 768px) {
  .popover-body {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
  }
}
</style>
