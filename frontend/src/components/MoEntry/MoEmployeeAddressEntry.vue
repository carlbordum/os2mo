<template>
  <mo-address-entry
    facet="employee_address_type"
    :value="value"
    :validityHidden="validityHidden"
    :required="required"
    :label="label"
    :preselectedType="preselectedType"
    :disabled-dates="disabledDates"
  />
</template>

<script>
/**
 * A manager address picker component.
 */

import { MoAddressEntry } from '@/components/MoEntry'

export default {
  name: 'MoEmployeeAddressEntry',
  extends: MoAddressEntry,

  components: {
    MoAddressEntry
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    facet: {
      type: String,
      required: false
    }
  }
}
</script>
