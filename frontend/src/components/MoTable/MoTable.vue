<template>
  <div>
    <mo-loader v-show="isLoading"/>
    <div v-show="!isLoading" class="scroll">
    <table v-if="!contentAvailable" class="table">
      <tbody>
      <tr>
        <td>
          <span>Intet at vise</span>
        </td>
      </tr>
      </tbody>
    </table>

    <b-form-checkbox-group v-model="selected">
    <table v-if="contentAvailable" class="table table-striped">
      <thead>
        <tr>
          <th v-if="multiSelect"></th>
          <th 
            scope="col" 
            v-for="(col, index) in columns" 
            :key="index"
          >
            {{$t('table_headers.'+col.label)}}
          </th>
          <th>{{$t('table_headers.start_date')}}</th>
          <th>{{$t('table_headers.end_date')}}</th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(c, index) in content" :key="index">
          <td v-if="multiSelect">
            <b-form-checkbox 
              class="checkbox-employee" 
              data-vv-as="checkbox" 
              :value="c"
            />
          </td>
          <td v-for="(col, index) in columns" :key="index">
            <mo-link 
              :value="c" 
              :column="col.data" 
              :field="col.field"
            />
          </td>
          <td>{{c.validity.from | date}}</td>
          <td>{{c.validity.to | date}}</td>
          <td>         
            <mo-entry-edit-modal 
              :type="type"
              :uuid="editUuid"
              :entry-component="editComponent"
              :content="c"
              :content-type="contentType"
            />
          </td>
        </tr>
      </tbody>
    </table>
      </b-form-checkbox-group>
    </div>
  </div>
</template>

<script>
  import '@/filters/GetProperty'
  import '@/filters/Date'
  import MoLoader from '@/components/atoms/MoLoader'
  import MoEntryEditModal from '@/components/MoEntryEditModal'
  import MoLink from '@/components/MoLink'

  export default {
    components: {
      MoLoader,
      MoLink,
      MoEntryEditModal
    },

    props: {
      content: Array,
      contentType: String,
      columns: Array,
      isLoading: Boolean,
      editComponent: Object,
      editUuid: String,
      multiSelect: Boolean,
      type: {
        type: String,
        required: true
      }
    },

    data () {
      return {
        selectAll: false,
        selected: []
      }
    },

    computed: {
      contentAvailable () {
        return this.content ? this.content.length > 0 : false
      }
    },

    watch: {
      selected (newVal) {
        this.$emit('selected-changed', newVal)
      }
    }
  }
</script>

<style scoped>
  table {
    margin-top: 0;
  }

  .scroll {
    max-height: 55vh;
    overflow-x: hidden;
    overflow-y: auto;
  }
</style>