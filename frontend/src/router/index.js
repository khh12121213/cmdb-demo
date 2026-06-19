import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/env',
    children: [
      { path: 'env', name: 'EnvManage', component: () => import('../views/EnvManage.vue'), meta: { title: '环境管理' } },
      { path: 'app', name: 'AppManage', component: () => import('../views/AppManage.vue'), meta: { title: '应用管理' } },
      { path: 'cluster', name: 'ClusterManage', component: () => import('../views/ClusterManage.vue'), meta: { title: '集群管理' } },
      { path: 'group', name: 'GroupManage', component: () => import('../views/GroupManage.vue'), meta: { title: '部署组管理' } },
      { path: 'instance', name: 'InstanceManage', component: () => import('../views/InstanceManage.vue'), meta: { title: '主机实例' } },
      { path: 'variable', name: 'VariableManage', component: () => import('../views/VariableManage.vue'), meta: { title: '变量配置' } },
      { path: 'release', name: 'ReleaseView', component: () => import('../views/ReleaseView.vue'), meta: { title: '发布基线/快照' } },
      { path: 'audit', name: 'AuditLog', component: () => import('../views/AuditLog.vue'), meta: { title: '审计日志' } },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
