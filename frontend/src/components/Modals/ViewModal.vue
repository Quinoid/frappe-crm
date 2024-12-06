<template>
  <Dialog
    v-model="show"
    :options="{
      title: editMode
        ? __('Edit View')
        : duplicateMode
          ? __('Duplicate View')
          : __('Create View'),
      actions: [
        {
          label: editMode
            ? __('Save Changes')
            : duplicateMode
              ? __('Duplicate')
              : __('Create'),
          class: 'bg-btn_primary hover:bg-btn_primary',
          variant: 'solid',
          onClick: () => (editMode ? update() : create()),
        },
      ],
    }"
  >
    <template #body-content>
      <div class="mb-1.5 block text-base text-gray-600">
        {{ __('View Name') }}
      </div>
      <div class="flex gap-2">
        <IconPicker v-model="view.icon" v-slot="{ togglePopover }">
          <Button
            variant="outline"
            size="md"
            class="flex size-8 text-2xl leading-none"
            :label="view.icon"
            @click="togglePopover"
          />
        </IconPicker>
        <TextInput
          class="flex-1"
          variant="outline"
          size="md"
          type="text"
          :placeholder="__('My Open Deals')"
          v-model="view.label"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import IconPicker from '@/components/IconPicker.vue'
import { call, TextInput } from 'qbs-vue-ui'
import { ref, watch, nextTick } from 'vue'
import { createToast } from '@/utils'
const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  options: {
    type: Object,
    default: {
      afterCreate: () => {},
      afterUpdate: () => {},
    },
  },
})

const show = defineModel()
const view = defineModel('view')

const editMode = ref(false)
const duplicateMode = ref(false)

const _view = ref({
  name: '',
  label: '',
  type: 'list',
  icon: '',
  filters: {},
  order_by: 'modified desc',
  columns: '',
  rows: '',
})

// async function create() {
//   view.value.doctype = props.doctype
//   let v = await call(
//     'crm.fcrm.doctype.crm_view_settings.crm_view_settings.create',
//     { view: view.value },
//   )
//   show.value = false
//   props.options.afterCreate?.(v)
// }
async function create() {
  try {
    view.value.doctype = props.doctype

    let v = await call(
      'crm.fcrm.doctype.crm_view_settings.crm_view_settings.create',
      { view: view.value },
    )

    show.value = false
    props.options.afterCreate?.(v)
  } catch (error) {
    console.error('Error creating view:', error)
    createToast({
      title: 'Error Creating View',
      message: error.message || 'An error occurred while creating the view.',
      icon: 'error',
      iconClasses: 'text-red-500',
    })
    // Display error to the user
    errorMessage.value =
      error.message || 'An error occurred while creating the view.'
  }
}
async function update() {
  try {
    view.value.doctype = props.doctype

    await call('crm.fcrm.doctype.crm_view_settings.crm_view_settings.update', {
      view: view.value,
    })

    show.value = false
    props.options.afterUpdate?.(view.value)
  } catch (error) {
    console.error('Error updating view:', error)
    // Display error to the user
    createToast({
      title: 'Error updating view',
      message: error.message || 'An error occurred while updating the view.',
      icon: 'error',
      iconClasses: 'text-red-500',
    })
    errorMessage.value =
      error.message || 'An error occurred while updating the view.'
  }
}

// async function update() {
//   view.value.doctype = props.doctype
//   await call('crm.fcrm.doctype.crm_view_settings.crm_view_settings.update', {
//     view: view.value,
//   })
//   show.value = false
//   props.options.afterUpdate?.(view.value)
// }

watch(show, (value) => {
  if (!value) return
  editMode.value = false
  duplicateMode.value = false
  nextTick(() => {
    _view.value = { ...view.value }
    if (_view.value.mode === 'edit') {
      editMode.value = true
    } else if (_view.value.mode === 'duplicate') {
      duplicateMode.value = true
    }
  })
})
</script>
