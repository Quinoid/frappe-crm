<template>
     <div  class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
    >
      <SearchEmpty class="h-[196px] w-[196px] "  />
      <span>{{ __('No {0} Found', [__(props.moduleName)]) }}</span>
            <span class="text-gray-700 text-center font-inter text-sm font-normal leading-[20px]">{{'Looks like we couldn’t find anything matching your search or filters. Try broadening your criteria or start fresh!' }}</span>  

      <Button :label="__('Clear Search & Filters')" class="bg-btn_primary text-white" @click="clearFunction">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
      
    </div>
  </div>
</template>
<script setup>
import SearchEmpty from './Icons/SearchEmpty.vue';
const props = defineProps({
  clearFunction: {
    type: Function,
    required: true,
    },

    moduleName: {
    type: String,
    required: true,
  }
  
})
</script>s