<template>
  <div>
    <div
      :class="[
        'flex flex-wrap gap-1 rounded-[8px] bg-white p-1 ',
        {
          'border border-gray-300': !editableOnClick, // Apply border when not in editable mode
          'hover:border-gray-300 hover:border': editableOnClick, // Apply hover effect when not in editable mode
        },
      ]"
    >
      <Button
        ref="emails"
        v-for="value in values"
        :key="value"
        :label="value"
        theme="gray"
        variant="subtle"
        class="rounded-[6px] text-primary_text chip-style"
        @keydown.delete.capture.stop="removeLastValue"
      >
        <template #suffix>
          <FeatherIcon
            class="h-3.5"
            name="x"
            @click.stop="removeValue(value)"
          />
        </template>
      </Button>
      <div class="flex-1">
        <Combobox v-model="selectedValue" nullable>
          <Popover class="w-full" v-model:show="showOptions">
            <template #target="{ togglePopover }">
              <ComboboxInput
                ref="search"
                class="search-input form-input w-full border-none bg-white hover:bg-white focus:border-none focus:!shadow-none focus-visible:!ring-0"
                type="text"
                :value="query"
                @blur="handleBlur"
                :placeholder="'Select one or more ' + label"
                @change="
                  (e) => {
                    query = e.target.value
                    showOptions = true
                  }
                "
                @click="showOptions = true"
                autocomplete="off"
                @focus="() => togglePopover()"
                @keydown.delete.capture.stop="removeLastValue"
              />
            </template>
            <template #body="{ isOpen }">
              <div v-show="isOpen">
                <div class="mt-1 rounded-lg bg-white py-1 text-base shadow-2xl">
                  <ComboboxOptions
                    class="my-1 max-h-[12rem] overflow-y-auto px-1.5"
                    static
                  >
                    <ComboboxOption
                      v-for="option in options"
                      :key="option.value"
                      :value="option"
                      v-slot="{ active }"
                    >
                      <li
                        :class="[
                          'flex cursor-pointer items-center rounded px-2 py-1 text-base',
                          { 'bg-gray-100': active },
                        ]"
                      >
                        <UserAvatar
                          class="mr-2"
                          :user="option.value"
                          size="lg"
                        />
                        <div class="flex flex-col gap-1 p-1 text-gray-800">
                          <div class="text-base font-medium">
                            {{ option.label }}
                          </div>
                          <div class="text-sm text-gray-600">
                            {{ option.value }}
                          </div>
                        </div>
                      </li>
                    </ComboboxOption>
                  </ComboboxOptions>
                </div>
              </div>
            </template>
          </Popover>
        </Combobox>
      </div>
    </div>
    <ErrorMessage class="mt-2 pl-2" v-if="error" :message="error" />
  </div>
</template>

<script setup>
import UserAvatar from '@/components/UserAvatar.vue'
import Popover from '@/components/qbs-vue-ui/Popover.vue'
import {
  Combobox,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
} from '@headlessui/vue'
import { watchDebounced } from '@vueuse/core'
import { createResource } from 'qbs-vue-ui'
import { computed, nextTick, ref } from 'vue'

const props = defineProps({
  validate: {
    type: Function,
    default: null,
  },
  errorMessage: {
    type: Function,
    default: (value) => `${value} is an Invalid value`,
  },
  custom_option: {
    type: String,
    default: null,
  },
  modelValue: {
    type: Array,
    default: [],
  },
  editableOnClick: {
    type: Boolean,
    default: false,
  },
  label: {
    type: String,
    default: ''
  },
  
  datatype: {
    type: String,
    default: null, // Add datatype for conditional behavior
  },
  data: {
    type: Object,
    default: null,
  },
})

// const values = defineModel()
const emit = defineEmits(['update:modelValue', 'change'])
const emails = ref([])
const search = ref(null)
const error = ref(null)
const query = ref('')
const text = ref('')
const showOptions = ref(false)

const values = computed({
  get: () => props.modelValue,
  set: (newValues) => {
    emit('update:modelValue', [...newValues])
    emit('change', [...newValues])
  },
})

const selectedValue = computed({
  get: () => '',
  set: (val) => {
    if (val?.value) {
      addValue(val.value)
    }
    query.value = ''
    showOptions.value = false
  },
})

// const selectedValue = computed({
//   get: () => query.value || '',
//   set: (val) => {
//     query.value = ''
//     if (val) {
//       showOptions.value = false
//     }
//     val?.value && addValue(val.value)
//   },
// })

watchDebounced(
  query,
  (val) => {
    val = val || ''
    if (text.value === val && options.value?.length) return
    text.value = val
    reload(val)
  },
  { debounce: 300, immediate: true },
)

const filterOptions = createResource({
  url: 'frappe.desk.search.search_link',
  method: 'POST',
  cache: [text.value, props.custom_option],
  params: { txt: text.value, docType: props.custom_option },
  transform: (data) => {
    let allData = data.map((option) => {
      return {
        label: option.label,
        value: option.value,
      }
    })
    return allData
  },
})

const options = computed(() => {
  let searchedContacts = filterOptions.data || []
  if (!searchedContacts.length && query.value) {
    searchedContacts.push({
      label: query.value,
      value: query.value,
    })
  }
  return searchedContacts
})

function reload(val) {
  filterOptions.update({
    params: { txt: val, doctype: props.custom_option },
  })
  filterOptions.reload()
}

// const addValue = (value) => {
//   error.value = null
//   if (value) {
//     const splitValues = value.split(',')
//     splitValues.forEach((value) => {
//       value = value.trim()
//       if (value) {
//         // check if value is not already in the values array
//         if (!values.value?.includes(value)) {
//           // check if value is valid
//           if (value && props.validate && !props.validate(value)) {
//             error.value = props.errorMessage(value)
//             return
//           }
//           // add value to values array
//           if (!values.value) {
//             values.value = [value]
//           } else {
//             values.value.push(value)
//           }
//           value = value.replace(value, '')
//         }
//       }
//     })
//     !error.value && (value = '')
//   }
// }

function addValue(value) {
  if (value && !values.value.includes(value)) {
    if (props.datatype === 'Email') {
      if (props.validate && !props.validate(value)) {
        error.value = props.errorMessage(value)
        return
      }
    }
    values.value = [...values.value, value]
  }
  query.value = ''
}

const removeValue = (value) => {
  values.value = values.value.filter((v) => v !== value)
}

const removeLastValue = () => {
  if (query.value) return

  let emailRef = emails.value[emails.value.length - 1]?.$el
  if (document.activeElement === emailRef) {
    values.value.pop()
    nextTick(() => {
      if (values.value.length) {
        emailRef = emails.value[emails.value.length - 1].$el
        emailRef?.focus()
      } else {
        setFocus()
      }
    })
  } else {
    emailRef?.focus()
  }
}

function setFocus() {
  search.value.$el.focus()
}

defineExpose({ setFocus })
</script>
