<template>
  <Dialog
    v-model="show"
    :options="{ size: isMobile ? 'full' : '5xl' }"
    class="z-40"
  >
    <template #body>
      <div
        :class="[
          'flex',
          isMobile ? 'flex-col' : 'flex-row',
          'h-[calc(100vh_-_8rem)]',
        ]"
      >
        <button
          v-if="isMobile"
          @click="showSidebar = !showSidebar"
          class="bg-gray-100 p-2 text-center text-lg font-medium text-gray-600 w-full"
        >
          {{ showSidebar ? 'Hide Menu' : 'Show Menu' }}
        </button>

        <div
          v-show="!isMobile || showSidebar"
          :class="[
            'shrink-0 flex flex-col bg-gray-50 p-2',
            isMobile ? 'w-full' : 'w-52',
          ]"
        >
          <h1 class="mb-3 px-2 pt-2 text-lg font-semibold">
            {{ __('Settings') }}
          </h1>
          <div v-for="(tab, index) in tabs" :key="index">
            <div
              v-if="!tab.hideLabel"
              class="mb-2 mt-3 flex cursor-pointer gap-1.5 px-1 text-base font-medium text-gray-600 transition-all duration-300 ease-in-out"
            >
              <span>{{ __(tab.label) }}</span>
            </div>
            <nav class="space-y-1">
              <SidebarLink
                v-for="i in tab.items"
                :key="i.label"
                :icon="i.icon"
                :label="__(i.label)"
                class="w-full"
                :class="
                  activeTab?.label == i.label
                    ? 'bg-white shadow-sm'
                    : 'hover:bg-gray-100'
                "
                @click="handleTabClick(i)"
              />
            </nav>
          </div>
        </div>
        <div class="flex flex-1 flex-col overflow-y-auto">
          <component
            :is="activeTab.component"
            :key="componentKey"
            v-if="activeTab"
            :is-password-set="isPasswordSet"
            :show-change-password-modal.sync="showChangePasswordModal"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import ERPNextIcon from '@/components/Icons/ERPNextIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import InviteMemberPage from '@/components/Settings/InviteMemberPage.vue'
import ProfileSettings from '@/components/Settings/ProfileSettings.vue'
import WhatsAppSettings from '@/components/Settings/WhatsAppSettings.vue'
import ERPNextSettings from '@/components/Settings/ERPNextSettings.vue'
import TwilioSettings from '@/components/Settings/TwilioSettings.vue'
import SidebarLink from '@/components/SidebarLink.vue'
import { isWhatsappInstalled } from '@/composables/settings'
import { Dialog, createResource } from 'qbs-vue-ui'
import { ref, markRaw, computed, onMounted } from 'vue'
import ChangePassword from '@/components/Settings/ChangePassword.vue'
const show = defineModel()
const showSidebar = ref(false)
const isPasswordSet = ref(false)
const showChangePasswordModal = ref(false)
const componentKey = ref(0)
const tabs = computed(() => {
  let _tabs = [
    {
      label: __('Settings'),
      hideLabel: true,
      items: [
        {
          label: __('Profile'),
          icon: ContactsIcon,
          component: markRaw(ProfileSettings),
        },
        {
          label: __('Invite Members'),
          icon: 'user-plus',
          component: markRaw(InviteMemberPage),
        },
        {
          label: isPasswordSet.value
            ? __('Change Password')
            : __('Set Password'),
          icon: 'user-plus',
          component: markRaw(ChangePassword),
        },
      ],
    },
    {
      label: __('Integrations'),
      items: [
        {
          label: __('Twilio'),
          icon: PhoneIcon,
          component: markRaw(TwilioSettings),
        },
        {
          label: __('WhatsApp'),
          icon: WhatsAppIcon,
          component: markRaw(WhatsAppSettings),
          condition: () => isWhatsappInstalled.value,
        },
        // {
        //   label: __('ERPNext'),
        //   icon: ERPNextIcon,
        //   component: markRaw(ERPNextSettings),
        // },
      ],
    },
  ]

  return _tabs.map((tab) => {
    tab.items = tab.items.filter((item) => {
      if (item.condition) {
        return item.condition()
      }
      return true
    })
    return tab
  })
})
const handleTabClick = (tab) => {
  componentKey.value += 1
  activeTab.value = {}
  showChangePasswordModal.value = false
  activeTab.value = tab
  if (tab.label === 'Change Password' || tab.label === 'Set Password') {
    showChangePasswordModal.value = true
  }
}
const checkPasswordStatus = async () => {
  try {
    const response = await createResource({
      url: 'crm.api.communication.is_password_set',
    })
    isPasswordSet.value = response.data ?? false
  } catch (error) {
    console.error('Failed to check password status:', error)
  }
}
onMounted(() => {
  checkPasswordStatus()
})

const activeTab = ref(tabs.value[0].items[0])
const isMobile = ref(window.innerWidth < 768)

window.addEventListener('resize', () => {
  isMobile.value = window.innerWidth < 768
})
</script>
