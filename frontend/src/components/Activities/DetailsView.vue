<template>
  <div
    v-if="fieldsLayout.data"
    class="flex flex-1 flex-col justify-between overflow-hidden p-4 w-4/5 gap-4"
  >
    <div class="flex flex-col overflow-y-auto shadow-sm rounded-md bg-white">
      <div
        class="flex h-10.5 cursor-copy items-center px-5 py-2.5 text-lg font-medium border-b"
        @click="copyToClipboard(doc.data.name)"
      >
        {{ __(doc.data.name) }}
      </div>
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
                class="size-12 avat_container"
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
            <div class="flex flex-col gap-2.5 truncate">
              <Tooltip :text="doc.data.lead_name || __('Set first name')">
                <div class="truncate text-2xl font-medium">
                  {{ doc.data.lead_name || __('Untitled') }}
                </div>
              </Tooltip>
              <div class="flex gap-1.5">
                <Tooltip v-if="callEnabled" :text="__('Make a call')">
                  <Button
                    class="h-7 w-7"
                    @click="
                      () =>
                        doc.data.mobile_no
                          ? makeCall(doc.data.mobile_no)
                          : errorMessage(__('No phone number set'))
                    "
                  >
                    <PhoneIcon class="h-4 w-4 text-primary_text" />
                  </Button>
                </Tooltip>
                <Tooltip :text="__('Send an email')">
                  <Button class="h-7 w-7">
                    <Email2Icon
                      class="h-4 w-4 text-primary_text"
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
                      class="h-4 w-4 text-primary_text"
                      @click="
                        doc.data.website
                          ? openWebsite(doc.data.website)
                          : errorMessage(__('No website set'))
                      "
                    />
                  </Button>
                </Tooltip>
              </div>
              <ErrorMessage :message="__(error)" />
            </div>
          </div>
        </template>
      </FileUploader>
      <SLASection
        v-if="doc.data.sla_status"
        v-model="doc.data"
        @updateField="updateField"
      />
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 md:grid-cols-1  gap-4 w-full">
      <div
        v-for="(section, i) in fieldsLayout.data"
        :key="section.label"
        class="flex flex-col shadow-sm rounded-md "
      >
        <Section
          :is-opened="section.opened"
          :label="section.label"
          :hideDrillDown="true"
        >
          <SectionFields
            :fields="section.fields"
            :isLastSection="true"
            v-model="doc.data"
            @update="updateField"
          />
          <template v-if="i == 0 && isManager()" #actions>
            <Button
              variant="ghost"
              class="w-7 mr-2"
              @click="showSidePanelModal = true"
            >
              <EditIcon class="h-4 w-4" />
            </Button>
          </template>
        </Section>
      </div>
    </div>
    <SidePanelModal
      v-if="showSidePanelModal"
      v-model="showSidePanelModal"
      @reload="() => fieldsLayout.reload()"
    />
  </div>
</template>
<script setup>
import Section from '@/components/Section.vue'
import SectionFields from '@/components/SectionFields.vue'
import { ref } from 'vue'
import { usersStore } from '@/stores/users'
import SidePanelModal from '@/components/Settings/SidePanelModal.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import { FileUploader, Dropdown, Tooltip, Avatar } from 'qbs-vue-ui'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import LinkIcon from '@/components/Icons/LinkIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import { errorMessage, openWebsite, copyToClipboard } from '@/utils'
import { globalStore } from '@/stores/global'
import { callEnabled } from '@/composables/settings'
import SLASection from '@/components/SLASection.vue'
const props = defineProps({
  doctype: {
    type: String,
    default: 'CRM Lead',
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
})
const showSidePanelModal = ref(false)
const { makeCall } = globalStore()

const { isManager } = usersStore()

const emit = defineEmits(['reload'])

const _doctype = ref(props.doctype)
</script>
