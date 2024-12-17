<template>
  <div class="flex h-full flex-col gap-8 p-8">
    <div class="flex flex-1 flex-col gap-4">
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
        <p v-if="errors.website" class="text-red-500 text-sm">
          {{ errors.website }}
        </p>
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
        <p v-if="errors.gst_no" class="text-red-500 text-sm">
          {{ errors.gst_no }}
        </p>
      </div>

      <!-- Save Button -->
    </div>
    <div class="flex !flex-row-reverse">
      <Button
        variant="solid"
        class=" bg-btn_primary"
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

const validateForm = () => {
  let isValid = true
  const validationErrors = {}

  // Website validation: must be a valid URL if provided
  if (
    form.value.website &&
    !/^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/.test(
      form.value.website,
    )
  ) {
    validationErrors.website = 'Please enter a valid website URL'
    isValid = false
  }

  // GST number validation: must follow GSTIN format if provided
  if (
    form.value.gst_no &&
    !/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(
      form.value.gst_no,
    )
  ) {
    validationErrors.gst_no = 'Please enter a valid GST number'
    isValid = false
  }

  errors.value = validationErrors
  return isValid
}

// Function to handle form submission
const updateCompany = async () => {
  errors.value = {} // Reset errors
  loading.value = true

  // Validate the form
  if (!validateForm()) {
    loading.value = false

    return
  }

  createResource({
    url: 'crm.api.communication.custom_edit_company',
    params: {
      name: form.value.name,
      website: form.value.website,
      city: form.value.city,
      state: form.value.state,
      country: form.value.country,
      gst_no: form.value.gst_no,
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
      form.value.name = data.name
      form.value.website = data.website
      form.value.city = data.city
      form.value.state = data.state
      form.value.country = data.country
      form.value.gst_no = data.gst_no
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
