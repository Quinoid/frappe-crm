<template>
  <div
    v-if="filteredSections"
    class="flex flex-1 flex-col justify-between overflow-hidden p-4 w-4/5 gap-4"
  >
    <div class="flex flex-col overflow-y-auto shadow-sm rounded-md bg-white">
      <div
        class="flex h-10.5 cursor-copy items-center px-5 py-2.5 text-lg font-medium border-b"
        @click="copyToClipboard(doc.data.name)"
      >
        {{ __(doc.data.name) }}
      </div>

      <div class="flex items-center justify-start gap-5 border-b p-5">
        <FileUploader
          @success="(file) => updateField('image', file.file_url)"
          :validateFile="validateFile"
        >
          <template #default="{ openFileSelector, error }">
            <div
              class="flex items-center justify-start gap-5 border-b px-5 py-2.5"
            >
              <div class="group relative size-12">
                <Avatar
                  size="3xl"
                  class="size-12"
                  :label="doc.data.first_name || __('Untitled')"
                  :image="doc.data.image"
                />
                <component
                  :is="doc.data.image ? Dropdown : 'div'"
                  v-bind="
                    doc.data.image
                      ? {
                          options: [
                            {
                              icon: 'upload',
                              label: doc.data.image
                                ? __('Change image')
                                : __('Upload image'),
                              onClick: openFileSelector,
                            },
                            {
                              icon: 'trash-2',
                              label: __('Remove image'),
                              onClick: () => updateField('image', ''),
                            },
                          ],
                        }
                      : { onClick: openFileSelector }
                  "
                  class="!absolute bottom-0 left-0 right-0"
                >
                  <div
                    class="z-1 absolute bottom-0.5 left-0 right-0.5 flex h-9 cursor-pointer items-center justify-center rounded-b-full bg-black bg-opacity-40 pt-3 opacity-0 duration-300 ease-in-out group-hover:opacity-100"
                    style="
                      -webkit-clip-path: inset(12px 0 0 0);
                      clip-path: inset(12px 0 0 0);
                    "
                  >
                    <CameraIcon class="size-4 cursor-pointer text-white" />
                  </div>
                </component>
              </div>
            </div>
          </template>
        </FileUploader>

        <div class="flex flex-col gap-2.5 truncate">
          <Tooltip :text="doc.data?.full_name">
            <div class="truncate text-2xl font-medium">
              {{ doc.data?.full_name || __('Untitled') }}
            </div>
          </Tooltip>
          <div class="flex justify-between items-center">
            <Button
              :label="__('Delete')"
              theme="red"
              size="sm"
              @click="deleteContact"
            >
              <template #prefix>
                <FeatherIcon name="trash-2" class="h-4 w-4" />
              </template>
            </Button>
            <div class="flex gap-1.5">
              <Tooltip v-if="callEnabled" :text="__('Make a call')">
                <Button class="h-7 w-7" @click="triggerCall">
                  <PhoneIcon class="h-4 w-4" />
                </Button>
              </Tooltip>
              <Tooltip :text="__('Send an email')">
                <Button class="h-7 w-7">
                  <Email2Icon
                    class="h-4 w-4"
                    @click="
                      doc.data.email
                        ? openEmailBox()
                        : errorMessage(__('No email set'))
                    "
                  />
                </Button>
              </Tooltip>
              <Tooltip :text="__('Go to website')">
                <Button class="h-7 w-7">
                  <LinkIcon
                    class="h-4 w-4"
                    @click="
                      doc.data.website
                        ? openWebsite(doc.data.website)
                        : errorMessage(__('No website set'))
                    "
                  />
                </Button>
              </Tooltip>
            </div>
            <template v-if="i == 0 && isManager()">
              <Button
                variant="ghost"
                class="w-7 mr-2"
                @click="showSidePanelModal = true"
              >
                <EditIcon class="h-4 w-4" />
              </Button>
            </template>
          </div>
        </div>
      </div>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 md:grid-cols-1 gap-4 w-full">
      <div
        v-for="(section, i) in filteredSections"
        :key="section.label"
        class="flex flex-col p-3 shadow-sm rounded-md bg-white"
      >
        <Section
          :is-opened="section.opened"
          :label="section.label"
          :hideDrillDown="true"
        >
          <template #actions>
            <Button
              v--if="i == 0 && isManager()"
              variant="ghost"
              class="w-7 mr-2"
              @click="showSidePanelModal = true"
            >
              <EditIcon class="h-4 w-4" />
            </Button>
          </template>
          <SectionFields
            :fields="section.fields"
            :isLastSection="true"
            v-model="doc.data"
            @update="updateField"
          />
        </Section>
      </div>
    </div>
    <SidePanelModal
      v-if="showSidePanelModal"
      v-model="showSidePanelModal"
      doctype="Contact"
      @reload="() => props.fieldsLayout.reload()"
    />
  </div>
</template>
<script setup>
import Section from '@/components/Section.vue'
import SectionFields from '@/components/SectionFields.vue'
import { ref, computed } from 'vue'
import { usersStore } from '@/stores/users'
import SidePanelModal from '@/components/Settings/SidePanelModal.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import { Tooltip, Avatar } from 'qbs-vue-ui'
import LinkIcon from '@/components/Icons/LinkIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import { errorMessage, openWebsite, copyToClipboard } from '@/utils'
import { globalStore } from '@/stores/global'
import { callEnabled } from '@/composables/settings'
import { useRouter } from 'vue-router'
import { FileUploader, Dropdown, call } from 'qbs-vue-ui'
import { createToast } from '@/utils'
const router = useRouter()
const props = defineProps({
  doctype: {
    type: String,
    default: 'Contact',
  },
  fieldsLayout: {
    type: Object,
    default: () => ({}),
  },
  doc: {
    type: Object,
    default: () => ({}),
  },
  updateField: {
    type: Function,
    default: () => {},
  },
  openEmailBox: {
    type: Function,
    default: () => {},
  },
  organization: {
    type: Object,
    default: () => ({}),
  },
  deleteContact: {
    type: Function,
    default: () => ({}),
  },
})
const showSidePanelModal = ref(false)
const { makeCall } = globalStore()
const _contact = ref({})
const _address = ref({})

const { isManager } = usersStore()

const emit = defineEmits(['reload'])

_contact.value = props.doc.data

const filteredSections = computed(() => {
  let allSections = props.fieldsLayout.data || []
  if (!allSections.length) return []

  allSections.forEach((s) => {
    s.fields.forEach((field) => {
      if (field.name == 'email_id') {
        field.type = props.doc?.data?.name ? 'Dropdown' : 'Data'
        field.options =
          props.doc.data?.email_ids?.map((email) => {
            return {
              name: email.name,
              value: email.email_id,
              selected: email.email_id === props.doc.data.email_id,
              placeholder: 'john@doe.com',
              onClick: () => {
                _contact.value.email_id = email.email_id
                _contact.value.email_ids = _contact.value.email_ids.map(
                  (emails) => ({
                    ...emails,
                    is_primary: emails.email_id === email.email_id ? 1 : 0,
                  }),
                )
                setAsPrimary('email', email.email_id)
              },
              onSave: (option, isNew) => {
                if (isNew) {
                  createNew('email', option.value)
                  if (props.doc.data.email_ids.length === 1) {
                    _contact.value.email_id = option.value
                  }
                } else {
                  if (props.doc.data.email_ids.length === 1) {
                    _contact.value.email_id = option.value
                  } else {
                    _contact.value.email_ids.find(
                      (emails) => emails.name === option.name,
                    ).email_id = option.value
                  }
                  editOption('Contact Email', option.name, option.value)
                }
              },
              onDelete: async (option, isNew) => {
                props.doc.data.email_ids = props.doc.data.email_ids.filter(
                  (email) => email.name !== option.name,
                )
                !isNew && (await deleteOption('Contact Email', option.name))
                if (_contact.value.email_id === option.value) {
                  if (props.doc.data.email_ids.length === 0) {
                    _contact.value.email_id = ''
                  } else {
                    _contact.value.email_id = props.doc.data.email_ids.find(
                      (email) => email.is_primary,
                    )?.email_id
                  }
                }
              },
            }
          }) || []
        field.create = () => {
          props.doc.data?.email_ids?.push({
            name: 'new-1',
            value: '',
            selected: false,
            isNew: true,
          })
        }
      } else if (
        field.name == 'mobile_no' ||
        field.name == 'actual_mobile_no'
      ) {
        field.type = props.doc?.data?.name ? 'Dropdown' : 'Data'
        field.name = 'actual_mobile_no'
        field.options =
          props.doc.data?.phone_nos?.map((phone) => {
            return {
              name: phone.name,
              value: phone.phone,
              selected: phone.phone === props.doc.data.actual_mobile_no,
              onClick: () => {
                _contact.value.actual_mobile_no = phone.phone
                _contact.value.mobile_no = phone.phone
                setAsPrimary('mobile_no', phone.phone)
              },
              onSave: (option, isNew) => {
                if (isNew) {
                  createNew('phone', option.value)
                  if (props.doc.data.phone_nos.length === 1) {
                    _contact.value.actual_mobile_no = option.value
                  }
                } else {
                  editOption('Contact Phone', option.name, option.value)
                }
              },
              onDelete: async (option, isNew) => {
                props.doc.data.phone_nos = props.doc.data.phone_nos.filter(
                  (phone) => phone.name !== option.name,
                )
                !isNew && (await deleteOption('Contact Phone', option.name))
                if (_contact.value.actual_mobile_no === option.value) {
                  if (props.doc.data.phone_nos.length === 0) {
                    _contact.value.actual_mobile_no = ''
                  } else {
                    _contact.value.actual_mobile_no =
                      props.doc.data.phone_nos.find(
                        (phone) => phone.is_primary_mobile_no,
                      )?.phone
                  }
                }
              },
            }
          }) || []
        field.create = () => {
          props.doc.data?.phone_nos?.push({
            name: 'new-1',
            value: '',
            selected: false,
            isNew: true,
          })
        }
      } else if (field.name == 'address') {
        field.create = (value, close) => {
          _contact.value.address = value
          _address.value = {}
          showAddressModal.value = true
          close()
        }
        field.edit = async (addr) => {
          _address.value = await call('frappe.client.get', {
            doctype: 'Address',
            name: addr,
          })
          showAddressModal.value = true
        }
      }
    })
  })

  return allSections
})
async function setAsPrimary(field, value) {
  let d = await call('crm.api.contact.set_as_primary', {
    contact: props.doc.data.name,
    field,
    value,
  })
  if (d) {
    props.doc.reload()
    createToast({
      title: 'Contact updated',
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  }
}

console.log(filteredSections)

async function createNew(field, value) {
  let d = await call('crm.api.contact.create_new', {
    contact: props.doc.data.name,
    field,
    value,
  })
  if (d) {
    props.doc.reload()
    createToast({
      title: 'Contact updated',
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  }
}

async function editOption(doctype, name, value) {
  let d = await call('frappe.client.set_value', {
    doctype,
    name,
    fieldname: doctype == 'Contact Phone' ? 'phone' : 'email_id',
    value,
  })

  if (d) {
    props.doc.reload()
    createToast({
      title: 'Contact updated',
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  }
}

async function deleteOption(doctype, name) {
  await call('frappe.client.delete', {
    doctype,
    name,
  })
  props.doc.reload()
  createToast({
    title: 'Contact updated',
    icon: 'check',
    iconClasses: 'text-green-600',
  })
}

const _doctype = ref(props.doctype)
</script>
