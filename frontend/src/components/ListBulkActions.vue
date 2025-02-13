<template>
  <EditValueModal v-if="showEditModal" v-model="showEditModal" :doctype="doctype" :selectedValues="selectedValues"
    @reload="reload" />
  <AssignmentModal v-if="showAssignmentModal" v-model="showAssignmentModal" v-model:assignees="bulkAssignees"
    :docs="selectedValues" :doctype="doctype" @reload="reload" />
</template>

<script setup>
import EditValueModal from '@/components/Modals/EditValueModal.vue'
import AssignmentModal from '@/components/Modals/AssignmentModal.vue'
import { setupListCustomizations, createToast } from '@/utils'
import { globalStore } from '@/stores/global'
import { capture } from '@/telemetry'
import { call } from 'qbs-vue-ui'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  doctype: {
    type: String,
    default: '',
  },
  options: {
    type: Object,
    default: () => ({
      hideEdit: false,
      hideDelete: false,
      hideAssign: false,
    }),
  },
})

const list = defineModel()

const router = useRouter()

const { $dialog, $socket } = globalStore()

const showEditModal = ref(false)
const selectedValues = ref([])
const unselectAllAction = ref(() => { })

function editValues(selections, unselectAll) {
  selectedValues.value = selections
  showEditModal.value = true
  unselectAllAction.value = unselectAll
}

function convertToDeal(selections, unselectAll) {
  $dialog({
    title: __('Convert to Deal'),
    message: __('Are you sure you want to convert {0} Lead(s) to Deal(s)?', [
      selections.size,
    ]),
    variant: 'solid',
    theme: 'blue',
    actions: [
      {
        label: __('Convert'),
        variant: 'solid',
        class: 'bg-btn_primary hover:bg-btn_primary',
        onClick: (close) => {
          capture('bulk_convert_to_deal')
          Array.from(selections).forEach((name) => {
            call('crm.fcrm.doctype.crm_lead.crm_lead.convert_to_deal', {
              lead: name,
            }).then(() => {
              createToast({
                title: __('Converted successfully'),
                icon: 'check',
                iconClasses: 'text-green-600',
              })
              list.value.reload()
              unselectAll()
              close()
            })
          })
        },
      },
    ],
  })
}

// function deleteValues(selections, unselectAll) {
//   $dialog({
//     title: __('Delete'),
//     message: __('Are you sure you want to delete {0} item(s)?', [
//       selections.size,
//     ]),
//     variant: 'solid',
//     theme: 'red',
//     actions: [
//       {
//         label: __('Delete'),
//         variant: 'solid',
//         class: 'bg-btn_primary hover:bg-btn_primary',
//         theme: 'red',
//         onClick: (close) => {
//           capture('bulk_delete')
//           call('frappe.desk.reportview.delete_items', {
//             items: JSON.stringify(Array.from(selections)),
//             doctype: props.doctype,
//           }).then(() => {
//             createToast({
//               title: __('Deleted successfully'),
//               icon: 'check',
//               iconClasses: 'text-green-600',
//             })
//             unselectAll()
//             list.value.reload()
//             close()
//           })
//         },

//       },
//     ],
//   })
// }
function removeATags(htmlString) {
  return htmlString.replace(/<a [^>]*>(.*?)<\/a>/g, '$1')
}
function deleteValues(selections, unselectAll) {
  const API_BASE_PATH = `${window.location.origin}/api/method/`

  $dialog({
    title: __('Delete'),
    message: __('Are you sure you want to delete {0} item(s)?', [
      selections.size,
    ]),
    variant: 'solid',
    theme: 'red',
    actions: [
      {
        label: __('Delete'),
        variant: 'solid',
        class: 'bg-btn_primary hover:bg-btn_primary',
        theme: 'red',
        async onClick(close) {
          try {
            capture('bulk_delete')
            console.log(JSON.stringify(Array.from(selections)),'saad')
            const response = await fetch(
              `${API_BASE_PATH}frappe.desk.reportview.delete_items`,
              {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-Frappe-CSRF-Token': window.csrf_token,
                },
                body: JSON.stringify({
                  items: JSON.stringify(Array.from(selections)),
                  doctype: props.doctype,
                }),
              },
            )
            if (!response) {
              throw new Error('Server did not return a valid response.')
            }
            const data = await response.json()
            if (data._server_messages) {
              let errorMessage = __('Failed to delete the selected items. Please try again.')
                try {
                  const serverMessages = JSON.parse(data._server_messages)
                  if (Array.isArray(serverMessages) && [0]) {
                    const parsedMessage = JSON.parse(serverMessages[0])
                    if (parsedMessage.message) {
                      errorMessage = removeATags(parsedMessage.message)
                    }
                  }
                } catch (parseError) {
                  console.error('Error parsing server response:', parseError)
                }
              

              // Show error toast
              createToast({
                title: 'Error',
                text: errorMessage,
                icon: 'x',
                iconClasses: 'text-red-600',
              })
              close()
            } else {

              createToast({
                title: __('Deleted successfully'),
                icon: 'check',
                iconClasses: 'text-green-600',
              })

              unselectAll()
              list.value.reload()
              close()
            }
          } catch (error) {
            console.error('Failed to delete items:', error)

            let errorMessage = __('Failed to delete the selected items. Please try again.')

            // Attempt to parse server error messages
            if (error.message) {
              try {
                const serverMessages = JSON.parse(error.message)
                if (Array.isArray(serverMessages) &&  [0]) {
                  const parsedMessage = JSON.parse(serverMessages[0])
                  if (parsedMessage.message) {
                    errorMessage = removeATags(parsedMessage.message)
                  }
                }
              } catch (parseError) {
                console.error('Error parsing server response:', parseError)
              }
            }

            // Show error toast
            createToast({
              title: 'Error',
              text: errorMessage,
              icon: 'x',
              iconClasses: 'text-red-600',
            })
            close()
          }
        },
      },
    ],
  })
}

const showAssignmentModal = ref(false)
const bulkAssignees = ref([])

function assignValues(selections, unselectAll) {
  showAssignmentModal.value = true
  selectedValues.value = selections
  unselectAllAction.value = unselectAll
}

function clearAssignemnts(selections, unselectAll) {
  $dialog({
    title: __('Clear Assignment'),
    message: __('Are you sure you want to clear assignment for {0} item(s)?', [
      selections.size,
    ]),
    variant: 'solid',
    theme: 'red',
    actions: [
      {
        label: __('Clear Assignment'),
        variant: 'solid',
        theme: 'red',
        class: 'bg-btn_primary hover:bg-btn_primary',

        onClick: (close) => {
          capture('bulk_clear_assignment')
          call('frappe.desk.form.assign_to.remove_multiple', {
            doctype: props.doctype,
            names: JSON.stringify(Array.from(selections)),
            ignore_permissions: true,
          }).then(() => {
            createToast({
              title: __('Assignment cleared successfully'),
              icon: 'check',
              iconClasses: 'text-green-600',
            })
            reload(unselectAll)
            close()
          })
        },
      },
    ],
  })
}

const customBulkActions = ref([])
const customListActions = ref([])

function bulkActions(selections, unselectAll) {
  let actions = []

  if (!props.options.hideEdit) {
    actions.push({
      label: __('Edit'),
      class: 'bg-btn_primary hover:bg-btn_primary',

      onClick: () => editValues(selections, unselectAll),
    })
  }

  if (!props.options.hideDelete) {
    actions.push({
      label: __('Delete'),
      class: 'bg-btn_primary hover:bg-btn_primary',

      onClick: () => deleteValues(selections, unselectAll),
    })
  }

  if (!props.options.hideAssign) {
    actions.push({
      label: __('Assign To'),
      class: 'bg-btn_primary hover:bg-btn_primary',

      onClick: () => assignValues(selections, unselectAll),
    })
    actions.push({
      label: __('Clear Assignment'),
      class: 'bg-btn_primary hover:bg-btn_primary',
      onClick: () => clearAssignemnts(selections, unselectAll),
    })
  }

  if (props.doctype === 'CRM Lead') {
    actions.push({
      label: __('Convert to Deal'),
      class: 'bg-btn_primary hover:bg-btn_primary',
      onClick: () => convertToDeal(selections, unselectAll),
    })
  }

  customBulkActions.value.forEach((action) => {
    actions.push({
      label: __(action.label),
      onClick: () =>
        action.onClick({
          list: list.value,
          selections,
          unselectAll,
          call,
          createToast,
          $dialog,
          router,
        }),
    })
  })
  return actions
}

function reload(unselectAll) {
  unselectAllAction.value?.()
  unselectAll?.()
  list.value?.reload()
}

onMounted(async () => {
  if (!list.value?.data) return
  let customization = await setupListCustomizations(list.value.data, {
    list: list.value,
    call,
    createToast,
    $dialog,
    $socket,
    router,
  })
  customBulkActions.value =
    customization?.bulkActions || list.value?.data?.bulkActions || []
  customListActions.value =
    customization?.actions || list.value?.data?.listActions || []
})

defineExpose({
  bulkActions,
  customListActions,
})
</script>
