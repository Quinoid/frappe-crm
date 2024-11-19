<template>
  <Dialog v-model="show" :options="dialogOptions">
    <template #body>
      <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-gray-900">
              {{ __(dialogOptions.title) || __('Untitled') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="isManager() || detailMode"
              variant="ghost"
              class="w-7"
              @click="detailMode ? (detailMode = false) : openQuickEntryModal()"
            >
              <EditIcon class="h-4 w-4" />
            </Button>
            <Button variant="ghost" class="w-7" @click="show = false">
              <FeatherIcon name="x" class="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div>
          <div v-if="detailMode" class="flex flex-col gap-3.5">
            <div
              v-for="field in detailFields"
              :key="field.name"
              class="flex h-7 items-center gap-2 text-base text-gray-800"
            >
              <div class="grid w-7 place-content-center">
                <component :is="field.icon" />
              </div>
              <div v-if="field.type == 'dropdown'">
                <Dropdown
                  :options="field.options"
                  class="form-control -ml-2 mr-2 w-full flex-1"
                >
                  <template #default="{ open }">
                    <Button
                      variant="ghost"
                      :label="event[field.name]"
                      class="dropdown-button w-full justify-between truncate hover:bg-white"
                    >
                      <div class="truncate">{{ event[field.name] }}</div>
                      <template #suffix>
                        <FeatherIcon
                          :name="open ? 'chevron-up' : 'chevron-down'"
                          class="h-4 text-gray-600"
                        />
                      </template>
                    </Button>
                  </template>
                </Dropdown>
              </div>
              <div v-else>{{ field.value }}</div>
            </div>
          </div>
          <Fields
            v-else-if="filteredSections"
            :sections="filteredSections"
            :data="_event"
          />
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div v-if="!detailMode" class="px-4 pb-7 pt-4 sm:px-6">
        <div class="space-y-2">
          <Button
            class="w-full bg-btn_primary text-white"
            v-for="action in dialogOptions.actions"
            :key="action.label"
            v-bind="action"
          >
            {{ __(action.label) }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import Fields from '@/components/Fields.vue'
import ContactIcon from '@/components/Icons/ContactIcon.vue'
import GenderIcon from '@/components/Icons/GenderIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import AddressIcon from '@/components/Icons/AddressIcon.vue'
import CertificateIcon from '@/components/Icons/CertificateIcon.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import Dropdown from '@/components/qbs-vue-ui/Dropdown.vue'
import { usersStore } from '@/stores/users'
import { capture } from '@/telemetry'
import { call, createResource } from 'qbs-vue-ui'
import { ref, nextTick, watch, computed } from 'vue'
import { createToast } from '@/utils'
import { useRouter } from 'vue-router'

const props = defineProps({
  event: {
    type: Object,
    default: {},
  },
  events: {
    type: Object,
    default: {},
  },
  options: {
    type: Object,
    default: {
      redirect: true,
      detailMode: false,
      afterInsert: () => {},
    },
  },
})

const { isManager } = usersStore()

const router = useRouter()
const show = defineModel()

const detailMode = ref(false)
const editMode = ref(false)
let _event = ref({})
const error = ref(null)

async function updateContact() {
  if (!dirty.value) {
    show.value = false
    return
  }
  if (!_event.value.starts_on) {
    error.value = __('Start Date is mandatory')
    return error.value
  }
  if (!_event.value.subject) {
    error.value = __('Subject is mandatory')
    return error.value
  }
  if (!_event.value.event_category) {
    error.value = __('Event Category is mandatory')
  }
  const values = { ..._event.value }

  if (
    _event.value.custom_participant &&
    _event.value.custom_participant?.length > 0
  ) {
    values.custom_participant = _event.value.custom_participant.map((p) => {
      return {
        event_custom_participant: p,
      }
    })
  }
  let name = await callSetValue(values)
  if (name) {
    capture('event_updated')
    props.events?.reload?.()
    show.value = false
  }
}

async function callSetValue(values) {
  const d = await call('frappe.client.set_value', {
    doctype: 'Event',
    name: props.event.name,
    fieldname: values,
  })
  return d.name
}

async function callInsertDoc() {
  error.value = null
  let data = { ..._event.value }
  if (!_event.value.starts_on) {
    error.value = __('Start Date is mandatory')
    return error.value
  }
  if (!_event.value.subject) {
    error.value = __('Subject is mandatory')
    return error.value
  }
  if (!_event.value.event_category) {
    error.value = __('Event Category is mandatory')
  }

  if (
    _event.value.custom_participant &&
    _event.value.custom_participant?.length > 0
  ) {
    data.custom_participant = _event.value.custom_participant.map((p) => {
      return {
        event_custom_participant: p,
      }
    })
  }
  console.log(data)
  const doc = await call('frappe.client.insert', {
    doc: {
      doctype: 'Event',
      ...data,
    },
  })
  if (doc.name) {
    capture('event_created')
    props.events?.reload?.()
    show.value = false
  }
}

const dialogOptions = computed(() => {
  let title = !editMode.value ? 'New Event' : 'Edit Event'

  let size = detailMode.value ? '' : 'xl'
  let actions = detailMode.value
    ? []
    : [
        {
          label: editMode.value ? 'Save' : 'Create',
          variant: 'solid',
          disabled: !dirty.value,
          onClick: () => (editMode.value ? updateContact() : callInsertDoc()),
        },
      ]

  return { title, size, actions }
})

const detailFields = computed(() => {
  let details = [
    {
      icon: ContactIcon,
      name: 'full_name',
      value:
        (_event.value.salutation ? _event.value.salutation + '. ' : '') +
        _event.value.full_name,
    },
    {
      icon: GenderIcon,
      name: 'gender',
      value: _event.value.gender,
    },
    {
      icon: Email2Icon,
      name: 'email_id',
      value: _event.value.email_id,
    },
    {
      icon: PhoneIcon,
      name: 'mobile_no',
      value: _event.value.actual_mobile_no,
    },
    {
      icon: OrganizationsIcon,
      name: 'company_name',
      value: _event.value.company_name,
    },
    {
      icon: CertificateIcon,
      name: 'designation',
      value: _event.value.designation,
    },
    {
      icon: AddressIcon,
      name: 'address',
      value: _event.value.address,
    },
  ]

  return details.filter((detail) => detail.value)
})

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['quickEntryFields', 'Event'],
  params: { doctype: 'Event', type: 'Quick Entry' },
  auto: true,
})

const filteredSections = computed(() => {
  let allSections = sections.data || []
  if (!allSections.length) return []

  return allSections?.map((section) => {
    return { ...section, columns: 1 }
  })
})

const dirty = computed(() => {
  return JSON.stringify(props.event) !== JSON.stringify(_event.value)
})

watch(
  () => show.value,
  (value) => {
    if (!value) return
    detailMode.value = props.options.detailMode
    if (props.event.name) {
      editMode.value = true
      _event.value = { ...props.event }
    } else {
      editMode.value = false
    }
  },
  { deep: true },
)

const showQuickEntryModal = defineModel('quickEntry')

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  nextTick(() => {
    show.value = false
  })
}
</script>

<style scoped>
:deep(:has(> .dropdown-button)) {
  width: 100%;
}
</style>
