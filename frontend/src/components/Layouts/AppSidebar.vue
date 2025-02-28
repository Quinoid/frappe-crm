<template>
  <div class="relative flex h-full flex-col  justify-between transition-all duration-300 ease-in-out bg-sidebar"
    :class="isSidebarCollapsed ? 'w-12 p-2' : 'w-[268px]'">
    <div>
      <UserDropdown :class="isSidebarCollapsed ? 'p-0' : 'p-4'" :isCollapsed="isSidebarCollapsed" />
    </div>
        <div class="flex-1 overflow-y-auto overflow-x-hidden scrollbar-hidden" :class=" isSidebarCollapsed ? '' : '  p-4'">

      <div class="mb-3 flex flex-col">
        <SidebarLink id="notifications-btn" :label="__('Notifications')" :icon="NotificationsIcon"
          :isCollapsed="isSidebarCollapsed" @click="() => toggleNotificationPanel()" :divider="false" class="relative">
          <template #right>
            <Badge v-if="
              !isSidebarCollapsed &&
              notificationsStore().unreadNotificationsCount
            " :label="notificationsStore().unreadNotificationsCount" variant="subtle" />
            <div v-else-if="notificationsStore().unreadNotificationsCount"
              class="absolute -left-1.5 top-1 z-20 h-[5px] w-[5px] translate-x-6 translate-y-1 rounded-full bg-gray-800 ring-1 ring-white" />
          </template>
        </SidebarLink>
      </div>
      <div v-for="view in allViews" :key="view.label">
        <div v-if="!view.hideLabel && isSidebarCollapsed && view.views?.length" class="mx-2 my-2 h-1 border-b" />
        <Section :label="view.name" :hideLabel="view.hideLabel" :fromSidemenu="true" :isOpened="view.opened">
          <template #header="{ opened, hide, toggle }">
            <div v-if="!hide"
              class="flex cursor-pointer gap-1.5 px-1 text-base font-medium text-gray-600 transition-all duration-300 ease-in-out"
              :class="isSidebarCollapsed
                  ? 'ml-0 h-0 overflow-hidden opacity-0'
                  : 'ml-1 mt-2 h-7 w-auto opacity-100 justify-between'
                " @click="toggle()">
       
              <span class="text-[14px]">{{ __(view.name) }}</span>
              <FeatherIcon name="chevron-right" class="h-4 w-4 text-gray-900 transition-all duration-300 ease-in-out"
                :class="{ 'rotate-90': opened }" />
            </div>
          </template>
          <nav class="flex flex-col gap-[7px]">
            <SidebarLink v-for="link in view.views" :icon="link.icon" :divider="link?.divider" :label="__(link.label)"
              :to="link.to" :isCollapsed="isSidebarCollapsed" />
          </nav>

        </Section>
      </div>
    </div>
    <div class="m-2 flex flex-col gap-1">
      <SidebarLink :isStatic="true" :label="isSidebarCollapsed ? __('Expand') : __('Collapse')" :isCollapsed="isSidebarCollapsed"
        @click="isSidebarCollapsed = !isSidebarCollapsed" class="">
        <template #icon>
          <span class="grid h-4.5 w-5 flex-shrink-0 place-items-center">
            <CollapseSidebar class="h-4.5 w-4.5 text-gray-700 hover:text-primary_text duration-300 ease-in-out"
              :class="{ '[transform:rotateY(180deg)]': isSidebarCollapsed }" />
          </span>
        </template>
      </SidebarLink>
      <a href="https://quinoid.com/" target="_blank" rel="noopener noreferrer" v-if="!isSidebarCollapsed" :class="[
        ' mt-auto flex items-center pl-[4px] pr-[14px] py-1 text-sm text-gray-700',
        !isSidebarCollapsed ? 'left-[2px]' : 'left-0',
      ]">
        <SideBarIcon />
      </a>

    </div>
    <Notifications />
  </div>
</template>

<script setup>
import CalendarIcon from '@/components/Icons/CalendarIcon.vue'
import CollapseSidebar from '@/components/Icons/CollapseSidebar.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import DashboardIcon from '@/components/Icons/DashboardIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import NotificationsIcon from '@/components/Icons/NotificationsIcon.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import PinIcon from '@/components/Icons/PinIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import Notifications from '@/components/Notifications.vue'
import Section from '@/components/Section.vue'
import SidebarLink from '@/components/SidebarLink.vue'
import UserDropdown from '@/components/UserDropdown.vue'
import { notificationsStore } from '@/stores/notifications'
import { viewsStore } from '@/stores/views'
import { useStorage } from '@vueuse/core'
import { FeatherIcon } from 'qbs-vue-ui'
import { computed, h } from 'vue'
import EmailIcon from '../Icons/EmailIcon.vue'
import SideBarIcon from './SideBarIcon.vue'
const { getPinnedViews, getPublicViews, getReportViews } = viewsStore()
const { toggle: toggleNotificationPanel } = notificationsStore()

const isSidebarCollapsed = useStorage('isSidebarCollapsed', false)

const links = [
  {
    label: 'Dashboard',
    icon: DashboardIcon,
    to: 'Dashboard',
  },
  {
    label: 'Leads',
    icon: LeadsIcon,
    to: 'Leads',
  },
  {
    label: 'Deals',
    icon: DealsIcon,
    to: 'Deals',
  },
  {
    label: 'Contacts',
    icon: ContactsIcon,
    to: 'Contacts',
  },
  {
    label: 'Organizations',
    icon: OrganizationsIcon,
    to: 'Organizations',
    divider: true,

  },
  {
    label: 'Notes',
    icon: NoteIcon,
    to: 'Notes',
  },
  {
    label: 'Tasks',
    icon: TaskIcon,
    to: 'Tasks',
  },

  {
    label: 'Call Logs',
    icon: PhoneIcon,
    to: 'Call Logs',
    divider: true,

  },

  {
    label: 'Email Templates',
    icon: Email2Icon,
    to: 'Email Templates',
  },
  {
    label: 'Emails',
    icon: EmailIcon,
    to: 'Emails',
    divider: true,

  },
  {
    label: 'Events',
    icon: CalendarIcon,
    to: 'Events',
        divider: true,

  },
]

const allViews = computed(() => {
  let _views = [
    {
      name: 'All Views',
      hideLabel: true,
      opened: true,
      views: links,
    },
  ]
  if (getPublicViews().length) {
    _views.push({
      name: 'Public views',
      opened: true,
      views: parseView(getPublicViews()),
    })
  }
  if (getReportViews().length) {
    _views.push({
      name: 'Reports',
      opened: true,
      views: parseView(getReportViews()),
    })
  }

  if (getPinnedViews().length) {
    _views.push({
      name: 'Pinned views',
      opened: true,
      views: parseView(getPinnedViews()),
    })
  }
  return _views
})

function parseView(views) {
  return views.map((view) => {
    return {
      label: view.label,
      icon: getIcon(view.route_name, view.icon),
      to: {
        name: view.route_name,
        params: { viewType: view.type || 'list' },
        query: { view: view.name },
      },
    }
  })
}

function getIcon(routeName, icon) {
  if (icon) return h('div', { class: 'size-auto' }, icon)

  switch (routeName) {
    case 'Leads':
      return LeadsIcon
    case 'Deals':
      return DealsIcon
    case 'Contacts':
      return ContactsIcon
    case 'Organizations':
      return OrganizationsIcon
    case 'Notes':
      return NoteIcon
    case 'Call Logs':
      return PhoneIcon
    case 'Calendar':
      return CalendarIcon
    case 'Dashboard':
      return DashboardIcon
    default:
      return PinIcon
  }
}
</script>
