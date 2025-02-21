<template>
  <div
    class="activity group flex h-48 cursor-pointer flex-col justify-between gap-2 rounded-md bg-white px-4 py-3 hover:bg-gray-100"
  >
    <div class="flex items-center justify-between">
      <div class="truncate text-lg font-medium">
        {{ note.title }}
      </div>
      <Dropdown
        :options="[
          {
            label: __('Delete'),
            icon: 'trash-2',
            onClick: () => deleteNote(note.name),
          },
        ]"
        @click.stop
        class="h-6 w-6"
      >
        <Button
          icon="more-horizontal"
          variant="ghosted"
          class="!h-6 !w-6 hover:bg-gray-100"
        />
      </Dropdown>
    </div>
    <TextEditor
      v-if="note.content"
      :content="note.content"
      :editable="false"
      editor-class="!prose-sm max-w-none !text-sm text-gray-600 focus:outline-none"
      class="flex-1 overflow-hidden"
    />
    <div class="mt-1 flex items-center justify-between gap-2">
      <div class="flex items-center gap-2 truncate">
        <UserAvatar :user="note.owner" size="xs" />
        <div
          class="truncate text-sm text-gray-800"
          :title="getUser(note.owner).full_name"
        >
          {{ getUser(note.owner).full_name }}
        </div>
      </div>
      <Tooltip :text="dateFormat(note.modified, dateTooltipFormat)">
        <div class="truncate text-sm text-gray-700">
          {{ __(timeAgo(note.modified)) }}
        </div>
      </Tooltip>
    </div>
  </div>
</template>
<script setup>
import UserAvatar from '@/components/UserAvatar.vue'
import { timeAgo, dateFormat, dateTooltipFormat } from '@/utils'
import { Tooltip, Dropdown, TextEditor, call } from 'qbs-vue-ui'
import { usersStore } from '@/stores/users'
const props = defineProps({
  note: Object,
  modelValue: {
    type: Object, // Ensure it's the resource object
    required: true,
  },
})

const { getUser } = usersStore()

// async function deleteNote(name) {
//   await call('frappe.client.delete', {
//     doctype: 'FCRM Note',
//     name,
//   })
//   notes.reload()
// }
async function deleteNote(name) {
  try {
    await call('frappe.client.delete', {
      doctype: 'FCRM Note',
      name,
    })
    props.modelValue.reload() // Refresh the notes
  } catch (error) {
    console.error('Failed to delete note:', error)
  }
}
</script>
