<template>
  <div class="flex h-full flex-col gap-8 p-8 items-center">
    <div class="w-1/2 flex flex-col gap-4 mt-8">
      <h2 class="text-xl font-semibold">Edit Company Details</h2>

      <div class="space-y-4">
        <!-- Name -->
        <FormControl
          label="Company Name"
          type="text"
          v-model="form.name"
          :error="errors.name"
          :disabled="true"
          aria-disabled="true"
        />

        <!-- Website -->
        <FormControl
          label="Website"
          type="url"
          v-model="form.website"
          :error="errors.website"
        />

        <!-- City -->
        <FormControl
          label="City"
          type="text"
          v-model="form.city"
          :error="errors.city"
        />

        <!-- State -->
        <FormControl
          label="State"
          type="text"
          v-model="form.state"
          :error="errors.state"
        />

        <!-- Country -->
        <FormControl
          label="Country"
          type="text"
          v-model="form.country"
          :error="errors.country"
        />

        <!-- GST Number -->
        <FormControl
          label="GST Number"
          type="text"
          v-model="form.gst_no"
          :error="errors.gst_no"
        />
      </div>

      <!-- Save Button -->
      <Button
        variant="solid"
        class="w-full bg-btn_primary"
        :loading="loading"
        @click="updateCompany"
        label="Save"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { createResource } from 'qbs-vue-ui'
import { createToast } from '@/utils'
const form = ref({
  name: '',
  website: '',
  city: '',
  state: '',
  country: '',
  gst_no: '',
})

const loading = ref(false)
const errors = ref({})

// Function to handle form submission
const updateCompany = async () => {
  errors.value = {} // Reset errors
  loading.value = true

  createResource({
    url: 'crm.api.communication.custom_edit_company',
    params: {
      doctype: 'User',
      name: form.value.name,
      email: form.value.email,
      phone: form.value.phone,
      address: form.value.address,
      city: form.value.city,
      state: form.value.state,
      zip: form.value.zip,
    },
    auto: true,
    onSuccess: (data) => {
      loading.value = false
      createToast({
        title: data.message,
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    },
    onError: () => {
      loading.value = false
    },
  })
}
const getCompany = async () => {
  createResource({
    url: 'crm.api.custom_doctype.get_company_details',

    auto: true,
    onSuccess: (data) => {
      console.log(data)
    },
    onError: () => {},
  })
}
getCompany()
</script>

<style scoped>
.flex {
  display: flex;
  flex-direction: column;
}
</style>
