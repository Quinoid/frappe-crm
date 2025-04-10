<template>
  <Teleport to="#app-header" v-if="showHeader">
    <slot>
      <header class="flex h-10.5 items-center justify-between py-[7px] pl-5">
        <div class="flex items-center gap-2">
          <slot name="left-header" />
        </div>
       
        <div
        :class="{
          'hidden md:hidden': hideRightHeader, 
          'lg:flex items-center gap-2': true
        }"
      >
          <slot name="right-header" class="flex items-center gap-2" />
        </div>
      </header>
    </slot>
  </Teleport>
</template>
<script setup>
import { nextTick, ref } from 'vue'

const showHeader = ref(false)

const props = defineProps({
  hideRightHeader: {
    type: Boolean,
    default: false,
  },
  
})
nextTick(() => {
  showHeader.value = true
})
</script>
