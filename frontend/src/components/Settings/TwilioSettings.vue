<template>
  <div>
    <SettingsPage v-if="!twiloSet" doctype="Twilio Settings" class="p-8" />
    <div
      class="flex flex-col gap-2 p-8 mt-[50px] items-center justify-center"
      v-else
    >
      <p>Setup your Twilio Agent Allocations</p>
      <a class="underline text-blue-500" href="/app/twilio-agents/view/list"
        >Click here</a
      >
    </div>
  </div>
</template>
<script setup>
import SettingsPage from '@/components/Settings/SettingsPage.vue'
import { call } from 'qbs-vue-ui'
import { ref } from 'vue'
const twiloSet = ref(false)
async function validateTwillo() {
  try {
    const res = await call('crm.api.communication.is_twilio_set')
    console.log(res)
    twiloSet.value = res.is_twilio_set
  } catch (error) {
    console.log(error)
  }
}
validateTwillo()
</script>
