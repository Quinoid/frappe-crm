import router from '@/router'
import { createResource } from 'qbs-vue-ui'

export const userResource = createResource({
  url: 'frappe.auth.get_logged_user',
  cache: 'User',
  onError(error) {
    if (error && error.exc_type === 'AuthenticationError') {
      router.push({ name: 'Home' })
    }
  },
})
