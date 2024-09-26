<template>
  <div
    class="grid items-center space-x-4 bg-table_header px-2 border-b-0 border border-table_border"
    :style="{
      gridTemplateColumns: getGridTemplateColumns(
        list.columns,
        list.options.selectable,
      ),
    }"
  >
    <Checkbox
      v-if="list.options.selectable"
      class="cursor-pointer duration-300"
      :modelValue="list.allRowsSelected"
      @click.stop="list.toggleAllRows"
    />
    <slot>
      <ListHeaderItem
        v-for="column in list.columns"
        :key="column.key"
        :item="column"
        @columnWidthUpdated="emit('columnWidthUpdated', column)"
      />
    </slot>
  </div>
</template>

<script setup>
import { Checkbox, ListHeaderItem } from 'frappe-ui'

import { getGridTemplateColumns } from './utils'
import { inject } from 'vue'

const emit = defineEmits(['columnWidthUpdated'])

const list = inject('list')
</script>
