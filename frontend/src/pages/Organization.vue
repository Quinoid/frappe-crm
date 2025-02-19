<template>
  <LayoutHeader v-if="organization.data">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <component
        :is="organization.data._assignedTo?.length == 1 ? 'Button' : 'div'"
      >
        <MultipleAvatar
          :avatars="organization.data._assignedTo"
          @click="showAssignmentModal = true"
        />
      </component>
      <Dropdown
        :options="statusOptions('organization', updateField, customStatuses)"
      >
        <template #default="{ open }">
          <Button
            :label="organization.data.organization_status"
            :class="'grey'"
          >
            <template #prefix>
              <IndicatorIcon />
            </template>
            <template #suffix>
              <FeatherIcon
                :name="open ? 'chevron-up' : 'chevron-down'"
                class="h-4"
              />
            </template>
          </Button>
        </template>
      </Dropdown>
    </template>
  </LayoutHeader>
  <div v-if="organization.data" class="flex h-full overflow-hidden">
    <Tabs v-model="tabIndex" :tabs="tabs">
      <template #tab="{ tab, selected }">
        <button
          class="group flex items-center gap-2 border-b border-transparent py-2.5 text-base text-gray-600 duration-300 ease-in-out hover:border-gray-400 hover:text-gray-900"
          :class="{ 'text-gray-900': selected }"
        >
          <component v-if="tab.icon" :is="tab.icon" class="h-5" />
          {{ __(tab.label) }}
          <Badge
            v-if="tab.label !== 'Details'"
            class="group-hover:bg-gray-900"
            :class="[selected ? 'bg-gray-900' : 'bg-gray-600']"
            variant="solid"
            theme="gray"
            size="sm"
          >
            {{ tab.count }}
          </Badge>
        </button>
      </template>
      <template #default="{ tab }">
        <div
          v-if="tab.label === 'Details'"
          class="pb-5  h-[calc(100vh-100px)] overflow-auto"
        >
          <OrgEdit
            class="mb-4"
            :doc="organization"
            v-if="tab.label === 'Details'"
            :fieldsLayout="fieldsLayout"
            :updateField="updateField"
            :deleteContact="deleteOrganization"
          />
        </div>
        <DealsListView
          class="mt-4"
          v-if="tab.label === 'Deals' && dealRows.length"
          :rows="dealRows"
          :columns="dealColumns"
          :options="{ selectable: false, showTooltip: false }"
        />
        <ContactsListView
          class="mt-4"
          v-if="tab.label === 'Contacts' && contactRows.length"
          :rows="contactRows"
          :columns="contactColumns"
          :options="{ selectable: false, showTooltip: false }"
        />
        <div
          v-if="!contactRows.length && tab.label === 'Contacts'"
          class="grid flex-1 place-items-center text-xl font-medium text-gray-500"
        >
          <div class="flex flex-col items-center justify-center space-y-3">
            <component :is="tab.icon" class="!h-10 !w-10" />
            <div>{{ __('No {0} Found', [__(tab.label)]) }}</div>
          </div>
        </div>
        <div
          v-if="!dealRows.length && tab.label === 'Deals'"
          class="grid flex-1 place-items-center text-xl font-medium text-gray-500"
        >
          <div class="flex flex-col items-center justify-center space-y-3">
            <component :is="tab.icon" class="!h-10 !w-10" />
            <div>{{ __('No {0} Found', [__(tab.label)]) }}</div>
          </div>
        </div>
      </template>
    </Tabs>
  </div>
  <div v-if="organization.data" class="flex flex-1 flex-col overflow-hidden">
    <FileUploader
      @success="changeOrganizationImage"
      :validateFile="validateFile"
    >
      <template #default="{ openFileSelector, error }">
        <div class="flex items-start justify-start gap-6 p-5 sm:items-center">
          <div class="group relative h-24 w-24">
            <Avatar
              size="3xl"
              :image="organization.data.organization_logo"
              :label="organization.data.name"
              class="!h-24 !w-24"
            />
            <component
              :is="organization.data.organization_logo ? Dropdown : 'div'"
              v-bind="
                organization.data.organization_logo
                  ? {
                      options: [
                        {
                          icon: 'upload',
                          label: organization.data.organization_logo
                            ? __('Change image')
                            : __('Upload image'),
                          onClick: openFileSelector,
                        },
                        {
                          icon: 'trash-2',
                          label: __('Remove image'),
                          onClick: () => changeOrganizationImage(''),
                        },
                      ],
                    }
                  : { onClick: openFileSelector }
              "
              class="!absolute bottom-0 left-0 right-0"
            >
              <div
                class="z-1 absolute bottom-0 left-0 right-0 flex h-13 cursor-pointer items-center justify-center rounded-b-full bg-black bg-opacity-40 pt-3 opacity-0 duration-300 ease-in-out group-hover:opacity-100"
                style="
                  -webkit-clip-path: inset(12px 0 0 0);
                  clip-path: inset(12px 0 0 0);
                "
              >
                <CameraIcon class="h-6 w-6 cursor-pointer text-white" />
              </div>
            </component>
          </div>
          <div class="flex flex-col justify-center gap-2 sm:gap-0.5">
            <div class="text-3xl font-semibold text-gray-900">
              {{ organization.data.name }}
            </div>
            <div
              class="flex flex-col flex-wrap gap-3 text-base text-gray-700 sm:flex-row sm:items-center sm:gap-2"
            >
              <div
                v-if="organization.data.website"
                class="flex items-center gap-1.5"
              >
                <WebsiteIcon class="h-4 w-4" />
                <span class="">{{ website(organization.data.website) }}</span>
              </div>
              <span
                v-if="organization.data.website"
                class="hidden text-3xl leading-[0] text-gray-600 sm:flex"
              >
                &middot;
              </span>
              <div
                v-if="organization.data.industry"
                class="flex items-center gap-1.5"
              >
                <FeatherIcon name="briefcase" class="h-4 w-4" />
                <span class="">{{ organization.data.industry }}</span>
              </div>
              <span
                v-if="organization.data.industry"
                class="hidden text-3xl leading-[0] text-gray-600 sm:flex"
              >
                &middot;
              </span>
              <div
                v-if="organization.data.territory"
                class="flex items-center gap-1.5"
              >
                <TerritoryIcon class="h-4 w-4" />
                <span class="">{{ organization.data.territory }}</span>
              </div>
              <span
                v-if="organization.data.territory"
                class="hidden text-3xl leading-[0] text-gray-600 sm:flex"
              >
                &middot;
              </span>
              <div
                v-if="organization.data.annual_revenue"
                class="flex items-center gap-1.5"
              >
                <MoneyIcon class="size-4" />
                <span class="">{{
                  formatNumberIntoCurrency(
                    organization.data.annual_revenue,
                    organization.data.currency,
                  )
                }}</span>
              </div>
              <span
                v-if="organization.data.annual_revenue"
                class="hidden text-3xl leading-[0] text-gray-600 sm:flex"
              >
                &middot;
              </span>
              <Button
                v-if="
                  organization.data.website ||
                  organization.data.industry ||
                  organization.data.territory ||
                  organization.data.annual_revenue
                "
                variant="ghost"
                :label="__('More')"
                class="w-fit cursor-pointer hover:text-gray-900 sm:-ml-1"
                @click="
                  () => {
                    detailMode = true
                    showOrganizationModal = true
                  }
                "
              />
            </div>
            <div class="mt-2 flex gap-1.5">
              <Button
                :label="__('Edit')"
                size="sm"
                @click="
                  () => {
                    detailMode = false
                    showOrganizationModal = true
                  }
                "
              >
                <template #prefix>
                  <EditIcon class="h-4 w-4" />
                </template>
              </Button>
              <Button
                :label="__('Delete')"
                theme="red"
                size="sm"
                @click="deleteOrganization"
              >
                <template #prefix>
                  <FeatherIcon name="trash-2" class="h-4 w-4" />
                </template>
              </Button>
            </div>
            <ErrorMessage class="mt-2" :message="__(error)" />
          </div>
        </div>
      </template>
    </FileUploader>
  </div>
  <OrganizationModal
    v-model="showOrganizationModal"
    v-model:quickEntry="showQuickEntryModal"
    v-model:organization="organization"
    :options="{ detailMode }"
  />
  <QuickEntryModal
    v-if="showQuickEntryModal"
    v-model="showQuickEntryModal"
    doctype="CRM Organization"
  />
  <AssignmentModal
    v-if="showAssignmentModal"
    v-model="showAssignmentModal"
    v-model:assignees="organization.data._assignedTo"
    :doc="organization.data"
    doctype="CRM Organization"
  />
</template>

<script setup>
import Icon from '@/components/Icon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import OrganizationModal from '@/components/Modals/OrganizationModal.vue'
import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
import DealsListView from '@/components/ListViews/DealsListView.vue'
import ContactsListView from '@/components/ListViews/ContactsListView.vue'
import WebsiteIcon from '@/components/Icons/WebsiteIcon.vue'
import TerritoryIcon from '@/components/Icons/TerritoryIcon.vue'
import MoneyIcon from '@/components/Icons/MoneyIcon.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import { globalStore } from '@/stores/global'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import MultipleAvatar from '../components/MultipleAvatar.vue'
import { Dropdown, Button } from 'qbs-vue-ui'
import { getView } from '@/utils/view'
import { createToast } from '@/utils'
import DocumentIcon from '@/components/Icons/DocumentIcon.vue'
import AssignmentModal from '@/components/Modals/AssignmentModal.vue'

import {
  dateFormat,
  dateTooltipFormat,
  timeAgo,
  formatNumberIntoCurrency,
} from '@/utils'
import {
  Breadcrumbs,
  Avatar,
  FileUploader,
  Tabs,
  call,
  createListResource,
  usePageMeta,
  createResource,
} from 'qbs-vue-ui'
import { h, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import OrgEdit from '@/components/Activities/OrgEdit.vue'
const props = defineProps({
  organizationId: {
    type: String,
    required: true,
  },
})
const { statusOptions, getContactStatus } = statusesStore()
const showAssignmentModal = ref(false)
const { $dialog } = globalStore()
const { getDealStatus } = statusesStore()
const showOrganizationModal = ref(false)
const showQuickEntryModal = ref(false)
const detailMode = ref(false)

const route = useRoute()
const router = useRouter()

const organization = createResource({
  url: 'crm.fcrm.doctype.crm_organization.api.get_organization',
  cache: ['CRM Organization', props.organizationId],
  params: {
    name: props.organizationId,
  },
  auto: true,
  transform: (data) => {
    let assignees = data._assign || []
    const nexData = data

    return {
      ...nexData,
      _assignedTo: assignees.map((user) => ({
        name: user,
        image: getUser(user).user_image,
        label: getUser(user).full_name,
      })),
    }
  },
})
const fieldsLayout = createResource({
  url: 'crm.api.doc.get_sidebar_fields',
  cache: ['fieldsLayout', props.organizationId],
  params: { doctype: 'CRM Organization', name: props.organizationId },
  auto: true,
})
function updateContact(fieldname, value, callback) {
  value = Array.isArray(fieldname) ? '' : value

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'CRM Organization',
      name: props.organizationId,
      fieldname: fieldname === 'status' ? 'organization_status' : fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      organization.reload()
      createToast({
        title: __('Organization updated'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      callback?.()
    },
    onError: (err) => {
      createToast({
        title: __('Error updating Organization'),
        text: __(err.messages?.[0]),
        icon: 'x',
        iconClasses: 'text-red-600',
      })
    },
  })
}
function updateField(name, value, callback) {
  let request = value
  if (
    (name === 'interested_services_for_lead' && value) ||
    (name === 'interested_services_for_deal' && value)
  ) {
    request = value?.map((item) => {
      return {
        link_field: item,
      }
    })
  }

  updateContact(name, request, () => {
    organization.data[name] = value
    callback?.()
  })
}
const breadcrumbs = computed(() => {
  let items = [{ label: __('Organizations'), route: { name: 'Organizations' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(
      route.query.view,
      route.query.viewType,
      'CRM Organization',
    )
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Organizations',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: props.organizationId,
    route: {
      name: 'Organization',
      params: { organizationId: props.organizationId },
    },
  })
  return items
})

usePageMeta(() => {
  return {
    title: props.organizationId,
  }
})

function validateFile(file) {
  let extn = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg', 'jpeg'].includes(extn)) {
    return __('Only PNG and JPG images are allowed')
  }
}

async function changeOrganizationImage(file) {
  await call('frappe.client.set_value', {
    doctype: 'CRM Organization',
    name: props.organizationId,
    fieldname: 'organization_logo',
    value: file?.file_url || '',
  })
  organization.reload()
}

function removeATags(htmlString) {
  return htmlString.replace(/<a [^>]*>(.*?)<\/a>/g, '$1')
}
async function deleteOrganization() {
  const API_BASE_PATH = `${window.location.origin}/api/method/`

  $dialog({
    title: __('Delete organization'),
    message: __('Are you sure you want to delete this organization?'),
    actions: [
      {
        label: __('Delete'),
        theme: 'red',
        variant: 'solid',
        async onClick(close) {
          try {
            const response = await fetch(
              `${API_BASE_PATH}crm.api.dashboard.custom_delete`,
              {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-Frappe-CSRF-Token': window.csrf_token,
                },
                body: JSON.stringify({
                  doctype: 'CRM Organization',
                  name: props.organizationId,
                }),
              },
            )

            if (!response.ok) {
              const errorData = await response.json()
              throw new Error(errorData._server_messages || response.statusText)
            }

            close()
            router.push({ name: 'Organizations' })
          } catch (error) {
            let errorMessage = __(
              'Failed to delete the organization. Please try again.',
            )

            // Parse server error message if availablne
            if (error.message) {
              try {
                const serverMessages = JSON.parse(error.message)
                if (Array.isArray(serverMessages) && serverMessages[0]) {
                  const parsedMessage = JSON.parse(serverMessages[0])
                  if (parsedMessage.message) {
                    // Clean the message to remove <a> tags
                    errorMessage = removeATags(parsedMessage.message)
                  }
                }
              } catch (parseError) {
                console.error(
                  'Failed to parse server error message:',
                  parseError,
                )
              }
            }
            // Show error toast
            createToast({
              title: 'Error',
              text: errorMessage,
              icon: 'x',
              iconClasses: 'text-red-600',
            })
            close()
          }
        },
      },
    ],
  })
}

function website(url) {
  return url && url.replace(/^(?:https?:\/\/)?(?:www\.)?/i, '')
}

const tabIndex = ref(0)
const tabs = [
  {
    label: 'Details',
    icon: DocumentIcon,
  },
  {
    label: 'Deals',
    icon: h(DealsIcon, { class: 'h-4 w-4' }),
    count: computed(() => deals.data?.length),
  },
  {
    label: 'Contacts',
    icon: h(ContactsIcon, { class: 'h-4 w-4' }),
    count: computed(() => contacts.data?.length),
  },
]

const { getUser } = usersStore()

const deals = createListResource({
  type: 'list',
  doctype: 'CRM Deal',
  cache: ['deals', props.organizationId],
  fields: [
    'name',
    'organization',
    'currency',
    'annual_revenue',
    'status',
    'email',
    'mobile_no',
    'deal_owner',
    'modified',
  ],
  filters: {
    organization: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

const contacts = createListResource({
  type: 'list',
  doctype: 'Contact',
  cache: ['contacts', props.organizationId],
  fields: [
    'name',
    'full_name',
    'image',
    'email_id',
    'mobile_no',
    'company_name',
    'modified',
  ],
  filters: {
    company_name: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

const dealRows = computed(() => {
  let list = []
  list = deals

  if (!list.data) return []

  return list.data.map((row) => {
    return getDealRowObject(row)
  })
})

const contactRows = computed(() => {
  let list = []
  list = contacts

  if (!list.data) return []

  return list.data.map((row) => {
    return getContactRowObject(row)
  })
})

function getDealRowObject(deal) {
  return {
    name: deal.name,
    organization: {
      label: deal.organization,
      logo: deal?.organization_logo,
    },
    annual_revenue: formatNumberIntoCurrency(
      deal.annual_revenue,
      deal.currency,
    ),
    status: {
      label: deal.status,
      color: getDealStatus(deal.status)?.iconColorClass,
    },
    email: deal.email,
    mobile_no: deal.mobile_no,
    deal_owner: {
      label: deal.deal_owner && getUser(deal.deal_owner).full_name,
      ...(deal.deal_owner && getUser(deal.deal_owner)),
    },
    modified: {
      label: dateFormat(deal.modified, dateTooltipFormat),
      timeAgo: __(timeAgo(deal.modified)),
    },
  }
}
console.log(organization.data, organization)
function getContactRowObject(contact) {
  return {
    name: contact.name,
    full_name: {
      label: contact.full_name,
      image_label: contact.full_name,
      image: contact.image,
    },
    email: contact.email_id,
    mobile_no: contact.mobile_no,
    company_name: {
      label: contact.company_name,
      logo: contact?.organization_logo,
    },
    modified: {
      label: dateFormat(contact.modified, dateTooltipFormat),
      timeAgo: __(timeAgo(contact.modified)),
    },
  }
}

const dealColumns = [
  {
    label: __('Organization'),
    key: 'organization',
    width: '11rem',
  },
  {
    label: __('Amount'),
    key: 'annual_revenue',
    width: '9rem',
  },
  {
    label: __('Status'),
    key: 'status',
    width: '10rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Mobile no'),
    key: 'mobile_no',
    width: '11rem',
  },
  {
    label: __('Deal owner'),
    key: 'deal_owner',
    width: '10rem',
  },
  {
    label: __('Last modified'),
    key: 'modified',
    width: '8rem',
  },
]

const contactColumns = [
  {
    label: __('Name'),
    key: 'full_name',
    width: '17rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Phone'),
    key: 'mobile_no',
    width: '12rem',
  },
  {
    label: __('Organization'),
    key: 'company_name',
    width: '12rem',
  },
  {
    label: __('Last modified'),
    key: 'modified',
    width: '8rem',
  },
]
</script>
