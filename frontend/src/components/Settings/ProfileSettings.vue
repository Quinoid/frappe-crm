<template>
  <div
    v-if="profile"
    class="flex w-full items-center justify-between p-12 pt-14"
  >
    <div class="flex items-center gap-4">
      <Avatar
        class="!size-16"
        :image="user.user_image"
        :label="user.full_name"
      />
      <div class="flex flex-col gap-1">
        <span class="text-2xl font-semibold">{{ user.full_name }}</span>
        <span class="text-base text-gray-700">{{ user.email }}</span>
      </div>
    </div>
    <Button :label="__('Edit profile')" @click="showProfileModal = true" />

    <Dialog
      :options="{ title: __('Edit Profile') }"
      v-model="showProfileModal"
      class="z-50"
      @after-leave="editingProfilePhoto = false"
    >
      <template #body-content>
        <div v-if="user" class="space-y-4">
          <ProfileImageEditor v-model="profile" v-if="editingProfilePhoto" />
          <template v-else>
            <div class="flex items-center gap-4">
              <Avatar
                size="lg"
                :image="profile.user_image"
                :label="profile.full_name"
              />
              <Button
                :label="__('Edit Profile Photo')"
                @click="editingProfilePhoto = true"
              />
            </div>
            <FormControl
              label="First Name"
              v-model="profile.first_name"
              :error="errors.first_name"
            />
            <FormControl
              label="Last Name"
              v-model="profile.last_name"
              :error="errors.last_name"
            />
            <FormControl
              label="Phone"
              v-model="profile.phone"
              :error="errors.phone"
            />
            <FormControl
              label="Email"
              v-model="profile.email"
              :disabled="true"
              aria-disabled="true"
              :error="errors.email"
            />
            <p v-if="errors" class="text-red-500 text-sm">
              {{ errors }}
            </p>
          </template>
        </div>
      </template>
      <template #actions>
        <Button
          v-if="editingProfilePhoto"
          class="mb-2 w-full"
          @click="editingProfilePhoto = false"
          :label="__('Back')"
        />
        <Button
          variant="solid"
          class="w-full bg-btn_primary"
          :loading="loading"
          @click="validateAndUpdateUser"
          :label="__('Save')"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import ProfileImageEditor from '@/components/Settings/ProfileImageEditor.vue'
import { usersStore } from '@/stores/users'
import { Dialog, Avatar, createResource } from 'qbs-vue-ui'
import { ref, computed, onMounted } from 'vue'

const { getUser, users } = usersStore()

const user = computed(() => getUser() || {})

const showProfileModal = ref(false)
const editingProfilePhoto = ref(false)
const profile = ref({})
const errors = ref('')
const loading = ref(false)

// Validation functions
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email) ? '' : 'Invalid email address.'
}

const validatePhone = (phone) => {
  const phoneRegex = /^[0-9]{10,15}$/
  return phoneRegex.test(phone) ? '' : 'Invalid phone number.'
}

const validateFields = () => {
  errors.value = profile.value.first_name ? '' : 'First Name is required.'
  errors.value = validatePhone(profile.value.phone)
  errors.value = validateEmail(profile.value.email)

  return !errors.value
}

function validateAndUpdateUser() {
  if (validateFields()) {
    loading.value = true
    const fieldname = {
      first_name: profile.value.first_name,
      last_name: profile.value.last_name,
      email: profile.value.email,
      phone: profile.value.phone,
      user_image: profile.value.user_image,
    }
    createResource({
      url: 'frappe.client.set_value',
      params: {
        doctype: 'User',
        name: user.value.name,
        fieldname,
      },
      auto: true,
      onSuccess: () => {
        loading.value = false
        showProfileModal.value = false
        users.reload()
      },
    })
  }
}

onMounted(() => {
  profile.value = { ...user.value }
})
</script>
