<template>
  <LayoutHeader v-if="contact.data">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <component :is="contact.data._assignedTo?.length == 1 ? 'Button' : 'div'">
        <MultipleAvatar
          :avatars="contact.data._assignedTo"
          @click="showAssignmentModal = true"
        />
      </component>
      <Dropdown
        :options="statusOptions('contact', updateField, customStatuses)"
      >
        <template #default="{ open }">
          <Button
            :label="contact.data.status"
            :class="getLeadStatus(contact.data.status).colorClass"
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
  <div v-if="contact.data" class="flex h-full flex-col overflow-hidden">
    <Tabs v-model="tabIndex" v-slot="{ tab }" :tabs="tabs">
      <Activities
        ref="activities"
        doctype="Contact"
        :title="tab.name"
        v-model:reload="reload"
        v-model:tabIndex="tabIndex"
        :contactId="contact.data.name"
        v-model="contact"
        :updateField="updateField"
        :updateFieldValue="updateFieldValue"
        :fieldsLayout="fieldsLayout"
        :deleteContact="deleteContact"
      />
    </Tabs>
  </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import { getView } from '@/utils/view'
import { globalStore } from '@/stores/global.js'
import { Breadcrumbs, Tabs, createResource, usePageMeta } from 'qbs-vue-ui'
import { ref, computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createToast } from '@/utils'
import Activities from '@/components/Activities/Activities.vue'
import DocumentIcon from '@/components/Icons/DocumentIcon.vue'
import { statusesStore } from '@/stores/statuses'
import MultipleAvatar from '@/components/MultipleAvatar.vue'

const { $dialog } = globalStore()
const { statusOptions, getLeadStatus } = statusesStore()

const props = defineProps({
  contactId: {
    type: String,
    required: true,
  },
})

const route = useRoute()
const router = useRouter()

const contact = createResource({
  url: 'crm.api.contact.get_contact',
  cache: ['contact', props.contactId],
  params: {
    name: props.contactId,
  },
  auto: true,
  transform: (data) => {
    return {
      ...data,
      actual_mobile_no: data.mobile_no,
      mobile_no: data.mobile_no,
    }
  },
})
function updateContact(fieldname, value, callback) {
  value = Array.isArray(fieldname) ? '' : value

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'Contact',
      name: props.contactId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      contact.reload()
      createToast({
        title: __('Contact updated'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      callback?.()
    },
    onError: (err) => {
      createToast({
        title: __('Error updating contact'),
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
    contact.data[name] = value
    callback?.()
  })
}
const fieldsLayout = createResource({
  url: 'crm.api.doc.get_sidebar_fields',
  cache: ['fieldsLayout', props.contactId],
  params: { doctype: 'Contact', name: props.contactId },
  auto: true,
})
const breadcrumbs = computed(() => {
  let items = [{ label: __('Contacts'), route: { name: 'Contacts' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'Contact')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Contacts',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: contact.data?.full_name,
    route: { name: 'Contact', params: { contactId: props.contactId } },
  })
  return items
})

usePageMeta(() => {
  return {
    title: contact.data?.full_name || contact.data?.name,
  }
})

function removeATags(htmlString) {
  return htmlString.replace(/<a [^>]*>(.*?)<\/a>/g, '$1')
}
async function deleteContact() {
  const API_BASE_PATH = `${window.location.origin}/api/method/`

  $dialog({
    title: __('Delete contact'),
    message: __('Are you sure you want to delete this contact?'),
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
                  doctype: 'Contact',
                  name: props.contactId,
                }),
              },
            )

            if (!response.ok) {
              const errorData = await response.json()
              throw new Error(errorData._server_messages || response.statusText)
            }

            close()
            router.push({ name: 'Contacts' })
          } catch (error) {
            let errorMessage = __(
              'Failed to delete the Contact. Please try again.',
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

const tabIndex = ref(0)
const tabs = [
  { label: 'Details', name: 'Details', icon: DocumentIcon },
  {
    label: 'Deals',
    name: 'Deals',
    icon: h(DealsIcon, { class: 'h-4 w-4' }),
    count: computed(() => deals.data?.length),
  },
]

const deals = createResource({
  url: 'crm.api.contact.get_linked_deals',
  cache: ['deals', props.contactId],
  params: {
    contact: props.contactId,
  },
  auto: true,
})
</script>

<style scoped>
:deep(.form-control input),
:deep(.form-control select),
:deep(.form-control button) {
  border-color: transparent;
  background: white;
}

:deep(.form-control button) {
  gap: 0;
}

:deep(.form-control button > div) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.form-control button svg) {
  color: white;
  width: 0;
}

:deep(:has(> .dropdown-button)) {
  width: 100%;
}

:deep(.dropdown-button > button > span) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
