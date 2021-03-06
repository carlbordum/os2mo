import { Selector } from 'testcafe'
import { baseURL } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('MoEmployeeMoveMany')
  .page(`${baseURL}/medarbejder/liste`)

const dialog = Selector('#employeeMoveMany')

const fromInput = dialog.find('input.form-control')

const parentFromInput = dialog.find('.from-unit input[data-vv-as="Flyt fra"]')

const parentToInput = dialog.find('.to-unit input[data-vv-as="Flyt til"]')

const checkboxInput = dialog.find('.checkbox-employee[data-vv-as="checkbox"]')

test('Workflow: moveMany employee', async t => {
  let today = moment()

  await t
    .setTestSpeed(0.8)
    .hover('#mo-workflow', { offsetX: 10, offsetY: 140 })
    .click('.btn-employee-moveMany')

    .expect(dialog.exists).ok('Opened dialog')

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(parentFromInput)
    .click(dialog.find('.from-unit span.tree-anchor')
      .withText('Hjørring'))

    .click(parentToInput)
    .click(dialog.find('.to-unit .tree-node')
      .withText('Hjørring')
      .find('.tree-arrow'))
    .click(dialog.find('.to-unit span.tree-anchor')
      .withText('Social og sundhed'))

    .click(checkboxInput)

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .match(
      /Medarbejderen med UUID [-0-9a-f]* er blevet flyttet/
    )
})
