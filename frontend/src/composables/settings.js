import { createResource, call } from 'qbs-vue-ui'
import { computed, ref } from 'vue'

export const whatsappEnabled = ref(false)
export const isWhatsappInstalled = ref(false)
createResource({
  url: 'crm.api.whatsapp.is_whatsapp_enabled',
  cache: 'Is Whatsapp Enabled',
  auto: true,
  onSuccess: (data) => {
    whatsappEnabled.value = Boolean(data)
  },
})
createResource({
  url: 'crm.api.whatsapp.is_whatsapp_installed',
  cache: 'Is Whatsapp Installed',
  auto: true,
  onSuccess: (data) => {
    isWhatsappInstalled.value = Boolean(data)
  },
})

export const callEnabled = ref(false)
createResource({
  url: 'crm.integrations.twilio.api.is_enabled',
  cache: 'Is Twilio Enabled',
  auto: true,
  onSuccess: (data) => {
    callEnabled.value = Boolean(data)
  },
})
export async function visibilityCheck(key) {
  try {
    // Call the API method with necessary arguments
    const res = await call('crm.api.dashboard.custom_record_count', {})
    const { limits } = res
    switch (key) {
      case 'twilo':
        return limits.twilio_feature === 1 ? true : false
      case 'whatsApp':
        return limits.whatsapp_feature === 1 ? true : false
      case 'calendar':
        return limits.calendar_feature === 1 ? true : false
      case 'email':
        return limits.email_feature === 1 ? true : false
      case 'custom_view_setup':
        return limits.custom_view_setup === 1 ? true : false
      case 'custom_field_setup':
        return limits.custom_field_setup === 1 ? true : false
      case 'custom_reports':
        return limits.custom_reports === 1 ? true : false
      default:
        return false
    }
  } catch (error) {
    console.log(error)
  }
}

export const mobileSidebarOpened = ref(false)

export const isMobileView = computed(() => window.innerWidth < 768)
