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

      <div class="flex items-center justify-start gap-5 border-b p-5">
        <Tooltip :text="__('Organization logo')">
          <div class="group relative size-12">
            <Avatar
              size="3xl"
              class="size-12 avat_container"
              :label="organization.data?.name || __('Untitled')"
              :image="organization.data?.organization_logo"
            />
          </div>
        </Tooltip>
        <div class="flex flex-col gap-2.5 truncate">
          <Tooltip :text="organization.data?.name || __('Set an organization')">
            <div class="truncate text-2xl font-medium">
              {{ organization.data?.name || __('Untitled') }}
            </div>
          </Tooltip>
          <div class="flex justify-between items-center">
            <div class="flex gap-1.5">
              <Tooltip v-if="callEnabled" :text="__('Make a call')">
                <Button class="h-7 w-7" @click="triggerCall">
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
      <SLASection
        v-if="doc.data.sla_status"
        v-model="doc.data"
        @updateField="updateField"
      />
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 md:grid-cols-1 gap-4 w-full">
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
          <template #actions>
            <div v-if="section.contacts" class="pr-2">
              <Link
                value=""
                doctype="Contact"
                from="deal_contact"
                @change="(e) => addContact(e)"
                :onCreate="
                  (value, close) => {
                    _contact = {
                      first_name: value,
                      company_name: doc.data.organization,
                    }
                    showContactModal = true
                    close()
                  }
                "
              >
                <template #target="{ togglePopover }">
                  <Button
                    class="h-7 px-3"
                    variant="ghost"
                    icon="plus"
                    @click="togglePopover()"
                  />
                </template>
              </Link>
            </div>
            <Button
              v-else-if="
                ((!section.contacts && i == 1) || i == 0) && isManager()
              "
              variant="ghost"
              class="w-7 mr-2"
              @click="showSidePanelModal = true"
            >
              <EditIcon class="h-4 w-4" />
            </Button>
          </template>
          <SectionFields
            v-if="section.fields"
            :fields="section.fields"
            :isLastSection="true"
            v-model="doc.data"
            @update="updateField"
          />
          <div v-else>
            <div
              v-if="dealContacts?.loading && dealContacts?.data?.length == 0"
              class="flex min-h-20 flex-1 items-center justify-center gap-3 text-base text-gray-500"
            >
              <LoadingIndicator class="h-4 w-4" />
              <span>{{ __('Loading...') }}</span>
            </div>
            <div
              v-else-if="dealContacts?.data?.length"
              v-for="(contact, i) in dealContacts.data"
              :key="contact.name"
            >
              <div class="px-2 pb-2.5" :class="[i == 0 ? 'pt-5' : 'pt-2.5']">
                <Section :is-opened="contact.opened">
                  <template #header="{ opened, toggle }">
                    <div
                      class="flex cursor-pointer items-center justify-between gap-2 pr-1 text-base leading-5 text-gray-700"
                    >
                      <div
                        class="flex h-7 items-center gap-2 truncate"
                        @click="toggle()"
                      >
                        <Avatar
                          :label="contact.full_name"
                          :image="contact.image"
                          size="md"
                        />
                        <div class="truncate">
                          {{ contact.full_name }}
                        </div>
                        <Badge
                          v-if="contact.is_primary"
                          class="ml-2"
                          variant="outline"
                          :label="__('Primary')"
                          theme="green"
                        />
                      </div>
                      <div class="flex items-center">
                        <Dropdown :options="contactOptions(contact)">
                          <Button
                            icon="more-horizontal"
                            class="text-gray-600"
                            variant="ghost"
                          />
                        </Dropdown>
                        <Button
                          variant="ghost"
                          @click="
                            router.push({
                              name: 'Contact',
                              params: { contactId: contact.name },
                            })
                          "
                        >
                          <ArrowUpRightIcon class="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" @click="toggle()">
                          <FeatherIcon
                            name="chevron-right"
                            class="h-4 w-4 text-gray-900 transition-all duration-300 ease-in-out"
                            :class="{ 'rotate-90': opened }"
                          />
                        </Button>
                      </div>
                    </div>
                  </template>
                  <div class="flex flex-col gap-1.5 text-base text-gray-800">
                    <div class="flex items-center gap-3 pb-1.5 pl-1 pt-4">
                      <Email2Icon class="h-4 w-4" />
                      {{ contact.email }}
                    </div>
                    <div class="flex items-center gap-3 p-1 py-1.5">
                      <PhoneIcon class="h-4 w-4" />
                      {{ contact.mobile_no }}
                    </div>
                  </div>
                </Section>
              </div>
              <div
                v-if="i != dealContacts.data.length - 1"
                class="mx-2 h-px border-t border-gray-200"
              />
            </div>
            <div
              v-else
              class="flex h-20 items-center justify-center text-base text-gray-600"
            >
              {{ __('No contacts added') }}
            </div>
          </div>
        </Section>
      </div>
    </div>
    <SidePanelModal
      v-if="showSidePanelModal"
      v-model="showSidePanelModal"
      doctype="CRM Deal"
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
import { Tooltip, Avatar } from 'qbs-vue-ui'
import LinkIcon from '@/components/Icons/LinkIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import { errorMessage, openWebsite, copyToClipboard } from '@/utils'
import { globalStore } from '@/stores/global'
import { callEnabled } from '@/composables/settings'
import Link from '@/components/Controls/Link.vue'
import SLASection from '@/components/SLASection.vue'
import { Dropdown } from 'qbs-vue-ui'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const props = defineProps({
  doctype: {
    type: String,
    default: 'CRM Deal',
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
  dealContacts: {
    type: Object,
    default: () => ({}),
  },
  addContact: {
    type: Function,
    default: () => {},
  },
  contactOptions: {
    type: Function,
    default: () => {},
  },
  togglePopover: {
    type: Function,
    default: () => {},
  },
  showContactModal: {
    type: Function,
    default: () => {},
  },
  _contact: {
    type: Object,
    default: () => ({}),
  },
})
const showSidePanelModal = ref(false)
const { makeCall } = globalStore()

const { isManager } = usersStore()

const emit = defineEmits(['reload'])

const _doctype = ref(props.doctype)
</script>
