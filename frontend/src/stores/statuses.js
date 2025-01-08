import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import { capture } from '@/telemetry'
import { defineStore } from 'pinia'
import { createListResource } from 'qbs-vue-ui'
import { h, reactive } from 'vue'

export const statusesStore = defineStore('crm-statuses', () => {
  let leadStatusesByName = reactive({})
  let dealStatusesByName = reactive({})
  let contactStatusesByName = reactive({})
  let communicationStatusesByName = reactive({})
  let organizationStatusesByName = reactive({})

  const leadStatuses = createListResource({
    doctype: 'CRM Lead Status',
    fields: ['name', 'color', 'position', 'lead_status'],
    orderBy: 'position asc',
    cache: 'lead-statuses',
    initialData: [],
    auto: true,
    transform(statuses) {
      for (let status of statuses) {
        status.colorClass = colorClasses(status.color)
        status.iconColorClass = colorClasses(status.color, true)
        status.name = status.lead_status
        leadStatusesByName[status.name] = status
      }
      return statuses
    },
  })
  const contactStatuses = createListResource({
    doctype: 'Contact Status',
    fields: ['name', 'color', 'position'],
    orderBy: 'position asc',
    cache: 'contact-statuses',
    initialData: [],
    auto: true,
    transform(statuses) {
      for (let status of statuses) {
        status.colorClass = colorClasses(status.color)
        status.iconColorClass = colorClasses(status.color, true)
        contactStatusesByName[status.name] = status
      }
      return statuses
    },
  })
  const organizationStatuses = createListResource({
    doctype: 'CRM Organization Status',
    fields: ['name', 'color', 'position'],
    orderBy: 'position asc',
    cache: 'organization-statuses',
    initialData: [],
    auto: true,
    transform(statuses) {
      for (let status of statuses) {
        status.colorClass = colorClasses(status.color)
        status.iconColorClass = colorClasses(status.color, true)
        organizationStatusesByName[status.name] = status
      }
      return statuses
    },
  })

  const dealStatuses = createListResource({
    doctype: 'CRM Deal Status',
    fields: ['name', 'color', 'position'],
    orderBy: 'position asc',
    cache: 'deal-statuses',
    initialData: [],
    auto: true,
    transform(statuses) {
      for (let status of statuses) {
        status.colorClass = colorClasses(status.color)
        status.iconColorClass = colorClasses(status.color, true)
        dealStatusesByName[status.name] = status
      }
      return statuses
    },
  })

  const communicationStatuses = createListResource({
    doctype: 'CRM Communication Status',
    fields: ['name'],
    cache: 'communication-statuses',
    initialData: [],
    auto: true,
    transform(statuses) {
      for (let status of statuses) {
        communicationStatusesByName[status.name] = status
      }
      return statuses
    },
  })

  function colorClasses(color, onlyIcon = false) {
    let textColor = `!text-${color}-600`
    if (color == 'black') {
      textColor = '!text-gray-900'
    } else if (['gray', 'green'].includes(color)) {
      textColor = `!text-${color}-700`
    }

    let bgColor = `!bg-${color}-100 hover:!bg-${color}-200 active:!bg-${color}-300`

    return [textColor, onlyIcon ? '' : bgColor]
  }

  function getLeadStatus(name) {
    if (!name) {
      name = leadStatuses.data[0].name
    }
    return leadStatusesByName[name]
  }
  function getContactStatus(name) {
    if (!name) {
      name = contactStatuses.data[0].name
    }
    return contactStatusesByName[name]
  }
  function getDealStatus(name) {
    if (!name) {
      name = dealStatuses.data[0].name
    }
    return dealStatusesByName[name]
  }

  function getCommunicationStatus(name) {
    if (!name) {
      name = communicationStatuses.data[0].name
    }
    return communicationStatuses[name]
  }
  function getOrganizationStatus(name) {
    if (!name) {
      name = organizationStatuses.data[0].name
    }
    return organizationStatusesByName[name]
  }

  function statusOptions(doctype, action, statuses = []) {
    let statusesByName =
      doctype == 'deal'
        ? dealStatusesByName
        : doctype == 'contact'
          ? contactStatusesByName
          : doctype == 'organization'
            ? organizationStatusesByName
            : leadStatusesByName

    if (statuses.length) {
      statusesByName = statuses.reduce((acc, status) => {
        acc[status] = statusesByName[status]
        return acc
      }, {})
    }

    let options = []
    for (const status in statusesByName) {
      options.push({
        label: statusesByName[status].name,
        value: statusesByName[status].name,
        icon: () =>
          h(IndicatorIcon, {
            class: statusesByName[status].iconColorClass,
          }),
        onClick: () => {
          capture('status_changed', { doctype, status })
          action && action('status', statusesByName[status].name)
        },
      })
    }
    return options
  }

  return {
    leadStatuses,
    dealStatuses,
    communicationStatuses,
    getLeadStatus,
    getContactStatus,
    getDealStatus,
    getCommunicationStatus,
    statusOptions,
    getOrganizationStatus,
    organizationStatuses,
  }
})
