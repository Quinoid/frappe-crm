<template>
  <div>
  <a
    v-if="shouldShowComponent"
    class="flex flex-col  cursor-pointer items-center text-[14px] duration-300 ease-in-out  sidemenu-item focus:outline-none focus:transition-none focus-visible:rounded focus-visible:ring-2 focus-visible:ring-gray-400"
    :class="isActive ? ' bg-sidebar_active  sideBar_shadow' : 'hover:bg-sidebar_hover '"
    @click.prevent="handleClick"
    :href="linkHref"
  >
    <div
      class="flex w-full items-center justify-between duration-300 ease-in-out"
      :class="isCollapsed ? `${!isStatic ? 'ml-[3px] p-1' : ''}` : 'px-2 py-2'"
    >
      <div class="flex items-center truncate">
        <Tooltip :text="label" placement="right" :disabled="!isCollapsed">
          <slot name="icon">
            <span class="grid flex-shrink-0 place-items-center">
              <FeatherIcon
                v-if="typeof icon == 'string'"
                :name="icon"
                class="size-5"
                  :class="isActive ?   'text-primary_text':'text-sidebar_icon_color'"

              />
                <component 
                  v-else 
                  :is="icon" 
                  class="size-5" 
                  :class="isActive ? 'text-primary_text':'text-sidebar_icon_color'"
                />
            </span>
          </slot>
        </Tooltip>
        <Tooltip
          :text="label"
          placement="right"
          :disabled="isCollapsed"
          :hoverDelay="1.5"
        >
          <span
            class="flex-1 flex-shrink-0 text-[#222222] truncate text-[14px] duration-300 ease-in-out"
            :class="
              isActive ? 'text-primary_text':'text-[#222222]',
              isCollapsed
                ? 'ml-0 w-0 overflow-hidden opacity-0'
                : 'ml-2 w-auto opacity-100'
            "
          >
            {{ label }}
          </span>
        </Tooltip>
      </div>
      <slot name="right" />
    </div>
  </a>
    <div v-if="divider" class="border-b border-gray-300 my-2"></div>
    </div>

</template>

<script setup>
import { isMobileView, mobileSidebarOpened } from '@/composables/settings'
import { call, Tooltip } from 'qbs-vue-ui'
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
const router = useRouter()
const route = useRoute()

const props = defineProps({
  icon: {
    type: [Object, String],
  },
  label: {
    type: String,
    default: '',
  },
  to: {
    type: [Object, String],
    default: '',
  },
  divider: {
    type: Boolean,
    default: false,
  },
  isStatic: {
    type: Boolean,
    default: false, 
  },
  isCollapsed: {
    type: Boolean,
    default: false,
  },
})

function handleClick() {
  if (!props.to) return
  if (typeof props.to === 'object') {
    router.push(props.to)
  } else {
    router.push({ name: props.to })
  }
  if (isMobileView.value) {
    mobileSidebarOpened.value = false
  }
}
const isTwilio = ref(false)
const isCalendar = ref(false)

const visibilityCheck = async () => {
  try {
    // Call the API method with necessary arguments
    const res = await call('crm.api.dashboard.custom_record_count', {})
    const { limits } = res
    isCalendar.value = limits.calendar_feature === 1 ? true : false
    isTwilio.value = limits.twilio_feature === 1 ? true : false
  } catch (error) {
    console.log(error)
  }
}
visibilityCheck()
const linkHref = computed(() => {
  if (!props.to) return '#'
  if (typeof props.to === 'object') {
    return props.to.href || router.resolve(props.to).href
  }
  return router.resolve({ name: props.to }).href
})

let isActive = computed(() => {
  if (route.query.view) {
    return route.query.view == props.to?.query?.view
  }

  return route.name === props.to || `${route.name}s` === props.to
})
const shouldShowComponent = computed(() => {
  if (!isTwilio.value && props.label === 'Call Logs') return false
  if (!isCalendar.value && props.label === 'Events') return false
  return true
})
</script>
