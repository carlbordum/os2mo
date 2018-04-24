import Vue from 'vue'
import Router from 'vue-router'
const LoginPage = () => import('@/login/LoginPage')
const MoBase = () => import('@/MoBase')
const Organisation = () => import('@/organisation/Organisation')
const OrganisationLandingPage = () => import('@/organisation/OrganisationLandingPage')
const OrganisationDetail = () => import('@/organisation/OrganisationDetail')
const Employee = () => import('@/employee/Employee')
const MoEmployeeList = () => import('@/employee/MoEmployeeList')
const EmployeeDetail = () => import('@/employee/EmployeeDetail')
const PageNotFound = () => import('@/components/PageNotFound')
const TheHelp = () => import('@/help/TheHelp')
const MoTimeMachine = () => import('@/timeMachine/MoTimeMachine')

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: LoginPage
    },
    {
      path: '',
      redirect: { name: 'Login' }
    },
    {
      path: '/',
      name: 'Base',
      component: MoBase,
      children: [
        {
          path: '/organisation',
          name: 'Organisation',
          component: Organisation,
          redirect: { name: 'OrganisationLandingPage' },

          children: [
            {
              path: '',
              name: 'OrganisationLandingPage',
              component: OrganisationLandingPage
            },
            {
              path: ':uuid',
              name: 'OrganisationDetail',
              component: OrganisationDetail
            }
          ]
        },
        {
          path: '/medarbejder',
          name: 'Employee',
          component: Employee,
          redirect: { name: 'EmployeeList' },

          children: [
            {
              path: 'liste',
              name: 'EmployeeList',
              component: MoEmployeeList
            },
            {
              path: ':uuid',
              name: 'EmployeeDetail',
              component: EmployeeDetail
            }
          ]
        },
        {
          path: '/hjaelp',
          name: 'Help',
          component: TheHelp
        },
        {
          path: '/tidsmaskine',
          name: 'Timemachine',
          component: MoTimeMachine
        },
        {
          path: '*',
          name: 'PageNotFound',
          component: PageNotFound
        }
      ]
    }
  ]
})
