<template>
  <form @submit.stop.prevent="createLeave">
    <mo-employee-picker v-model="employee" required/>

    <mo-leave-entry class="mt-3" v-model="leave"/>

    <div class="alert alert-danger" v-if="backendValidationError">
      {{$t('alerts.error.' + backendValidationError)}}
    </div>

    <div class="float-right">
      <button-submit :is-loading="isLoading"/>
    </div>
  </form>
</template>

<script>
/**
 * A employee create leave component.
 */

import { mapFields } from 'vuex-map-fields'
import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
import { MoLeaveEntry } from '@/components/MoEntry'
import ButtonSubmit from '@/components/ButtonSubmit'
import ValidateForm from '@/mixins/ValidateForm'
import store from './_store/employeeLeave.js'

const STORE_KEY = '$_employeeLeave'

export default {
  mixins: [ValidateForm],

  components: {
    MoEmployeePicker,
    MoLeaveEntry,
    ButtonSubmit
  },
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },

  computed: {
    /**
     * Get mapFields from vuex store.
     */
    ...mapFields(STORE_KEY, [
      'employee',
      'leave',
      'isLoading',
      'backendValidationError'
    ])
  },
  beforeCreate () {
    if (!(STORE_KEY in this.$store._modules.root._children)) {
      this.$store.registerModule(STORE_KEY, store)
    }
  },
  beforeDestroy () {
    this.$store.unregisterModule(STORE_KEY)
  },

  watch: {
    show (val) {
      if (!val) {
        this.onHidden()
      }
    }
  },

  methods: {
    /**
     * Create leave and check if the data fields are valid.
     * Then throw a error if not.
     */
    createLeave () {
      let vm = this
      if (this.formValid) {
        this.$store.dispatch(`${STORE_KEY}/leaveEmployee`)
          .then(() => {
            vm.$emit('submitted')
          })
      } else {
        this.$validator.validateAll()
      }
    },

    onHidden () {
      this.$store.dispatch(`${STORE_KEY}/resetFields`)
    }
  }
}
</script>
