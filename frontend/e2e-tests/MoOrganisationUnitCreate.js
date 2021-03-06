import { Selector } from 'testcafe'
import { baseURL } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('MoOrganisationUnitCreate')
  .page(`${baseURL}/organisation/97337de5-6096-41f9-921e-5bed7a140d85`)

const dialog = Selector('#orgUnitCreate')

const unitSelect = dialog.find('select[data-vv-as="Enhedstype"]')
const unitOption = unitSelect.find('option')

const addressInput = dialog.find('.v-autocomplete[data-vv-as="Adresse"]')
const addressItem = addressInput.find('.v-autocomplete-list-item label')

const parentInput = dialog.find('input[data-vv-as="Angiv overenhed"]')

const fromInput = dialog.find('.from-date input.form-control')

// const newDate = dialog.find('.btn-link')
// const newDateInput = dialog.find('.address-date input.form-control')

test('Workflow: create unit', async t => {
  let today = moment()

  // Some notes:
  //
  // You may notice that we have a few 'expects' waiting for an
  // autocomplete to be visible. They exist to ensure that the
  // autocomplete is properly rendered prior to attempting to select
  // an item. This can occur when TestCafe runs at full speed.
  //
  // Likewise, not hovering over an item prior to clicking it can lead
  // to the click not having any effect.
  //
  // We do autocomplete selection using the keyboard. In order to make
  // this work, we use our own, fixed, version of 'v-autocomplete'
  // that suppresses form submit in these cases.
  //
  // I quite deliberately added a lot of expects that verify that e.g.
  // selecting something in a drop-down has the desired effect. This
  // ensures that we yield more helpful error messages should the test
  // fail, rather than merely failing at form submit.

  await t
    .setTestSpeed(0.8)
    .hover('#mo-workflow', { offsetX: 10, offsetY: 10 })
    .click('.btn-unit-create')

    .expect(dialog.exists).ok('Opened dialog')

    .typeText(dialog.find('input[data-vv-as="Navn"]'), 'Hjørring VM 2018')

    .click(unitSelect)
    .click(unitOption.withText('Fagligt center'))

    .click(parentInput)
    .click(dialog.find('li.tree-node span.tree-anchor span'))

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(addressInput)
    .typeText(addressInput.find('input'), 'hovedvejen 2')
    .expect(addressItem.withText(' ').visible).ok()
    .pressKey('down enter')
    .expect(addressInput.find('input').value)
    .eql('Hovedvejen 2A, Tornby, 9850 Hirtshals')

    // .click(newDate)
    // .click(newDateInput)
    // .hover(dialog.find('.address-date .vdp-datepicker .day:not(.blank)')
    //        .withText(today.date().toString()))
    // .click(dialog.find('.address-date .vdp-datepicker .day:not(.blank)')
    //        .withText(today.date().toString()))
    // .expect(newDateInput.value).eql(today.format('DD-MM-YYYY'))

    .typeText(dialog.find('input[data-vv-as="Tlf"]'), '44772000')

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .match(
      /Organisationsenheden med UUID [-0-9a-f]* er blevet oprettet/
    )
  // TODO: verify that the unit was actually created, somehow?
})
