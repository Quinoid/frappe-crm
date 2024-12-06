<template>
  <div>
    <SettingsPage doctype="Twilio Settings" class="p-8" />
    <div class="pl-8" v-if="twiloSet">
      <a href="/app/twilio-agents/view/list"
        >Setup your Twilio Agent Allocations</a
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
