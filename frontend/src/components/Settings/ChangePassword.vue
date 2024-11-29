<template>
  <!-- <Dialog
    :options="{
      title: isPasswordSet ? __('Change Password') : __('Set Password'),
    }"
    @update:model-value="showChangePasswordModal = $event"
    v-model="localShow"
    class="z-50"
    @after-leave="
      () => {
        passwords.new_password = ''
        passwords.confirm_password = ''
        passwords.old_password = ''
      }
    "
  >
   -->
  <div class="flex h-full flex-col gap-8 p-8 items-center">
    <div class="w-1/2 flex flex-col gap-4 mt-8">
      <h2 class="flex gap-2 text-xl font-semibold leading-none h-5">
        {{ isPasswordSet ? __('Change Password') : __('Set Password') }}
      </h2>

      <div class="space-y-4">
        <div class="flex items-center gap-4"></div>
        <FormControl
          v-if="isPasswordSet"
          label="Old Password"
          type="password"
          v-model="passwords.old_password"
        />
        <FormControl
          label="New Password"
          type="password"
          v-model="passwords.new_password"
        />
        <p v-if="passwordStrengthError" class="text-red-500 text-sm">
          {{ passwordStrengthError }}
        </p>
        <FormControl
          label="Confirm Password"
          type="password"
          v-model="passwords.confirm_password"
        />
        <p v-if="error" class="text-red-500 text-sm">
          {{ error }}
        </p>
      </div>
      <p class="text-[10px] text-gray-600">
        Password should contain at least one uppercase letter, one lowercase
        letter, one digit, and one special character, with a minimum length of
        eight characters, and must not contain any spaces.
      </p>
      <Button
        variant="solid"
        class="w-full bg-btn_primary"
        :loading="loading"
        @click="updatePassword"
        :label="__('Save')"
      />
    </div>
  </div>
  <!-- </Dialog> -->
</template>
<script setup>
import { createResource } from 'qbs-vue-ui'
import { ref, computed } from 'vue'
import { createToast } from '@/utils'
const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
  isPasswordSet: {
    type: Boolean,
    required: false,
  },
})

const passwords = ref({
  new_password: '',
  confirm_password: '',
  old_password: '',
})
const loading = ref(false)
const error = ref('')
// const isPasswordSet = ref(false)
const emit = defineEmits(['update:showChangePasswordModal'])

// Local state for modal visibility

// Watch for prop changes and sync with local state

// Watch for local state changes and emit to parent

const passwordStrengthError = ref('')
function updatePassword() {
  // Reset errors
  error.value = ''
  passwordStrengthError.value = ''
  if (props.isPasswordSet) {
    if (!passwords.value.old_password || passwords.value.old_password == '') {
      error.value = 'Old Password is required.'
      return
    }
  }
  const strengthError = validatePasswordStrength(passwords.value.new_password)
  if (strengthError) {
    passwordStrengthError.value = strengthError
    return
  }
  // Check if passwords match
  if (passwords.value.new_password !== passwords.value.confirm_password) {
    error.value = 'Passwords do not match.'
    return
  }

  // Check password strength

  // Proceed with password update
  loading.value = true

  createResource({
    url: 'crm.api.communication.change_password',
    params: {
      doctype: 'User',
      old_password: passwords.value.old_password ?? undefined,
      new_password: passwords.value.new_password ?? '',
      confirm_password: passwords.value.confirm_password ?? '',
    },
    auto: true,
    onSuccess: () => {
      loading.value = false
      createToast({
        title: 'Password updated successfully',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    },
    onError: () => {
      loading.value = false
    },
  })
}
const MIN_LENGTH = 8
const MAX_LENGTH = 20

const validatePasswordStrength = (password) => {
  const rules = [
    {
      regex: /.{8,20}/,
      message: `Password must be between ${MIN_LENGTH} and ${MAX_LENGTH} characters.`,
    },
    {
      regex: /[A-Z]/,
      message: 'Password must contain at least one uppercase letter.',
    },
    {
      regex: /[a-z]/,
      message: 'Password must contain at least one lowercase letter.',
    },
    { regex: /[0-9]/, message: 'Password must contain at least one digit.' },
    {
      regex: /[\W_]/,
      message: 'Password must contain at least one special character.',
    },
  ]

  for (const rule of rules) {
    if (!rule.regex.test(password)) return rule.message
  }
  return ''
}

const hasErrors = computed(() => !!error.value || !!passwordStrengthError.value)
</script>
