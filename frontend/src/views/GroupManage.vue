<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>部署分组管理</span>
          <el-button type="primary" @click="openDialog()">新增分组</el-button>
        </div>
      </template>
      <div style="margin-bottom:12px;display:flex;gap:12px;flex-wrap:wrap">
        <el-select v-model="filterEnv" placeholder="环境" clearable style="width:120px" @change="fetch">
          <el-option v-for="e in envOptions" :key="e.env_code" :label="e.env_code" :value="e.env_code" />
        </el-select>
        <el-input v-model="filterApp" placeholder="应用编码" clearable style="width:140px" @change="fetch" />
        <el-input v-model="filterCluster" placeholder="集群ID" clearable style="width:100px" @change="fetch" />
        <el-select v-model="filterGroupType" placeholder="分组类型" clearable style="width:130px" @change="fetch">
          <el-option value="fixed" label="虚拟机(fixed)" />
          <el-option value="elastic" label="容器(elastic)" />
        </el-select>
        <el-select v-model="filterLock" placeholder="发布锁" clearable style="width:120px" @change="fetch">
          <el-option value="1" label="发布中" />
          <el-option value="0" label="空闲" />
        </el-select>
      </div>
      <el-table :data="tableData" v-loading="loading" stripe :row-class-name="rowClass">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="env_code" label="环境" width="70" />
        <el-table-column prop="app_code" label="应用" width="100" />
        <el-table-column prop="group_code" label="分组编码" width="120" />
        <el-table-column prop="group_name" label="分组名称" width="110" />
        <el-table-column prop="group_type" label="类型" width="70">
          <template #default="{row}"><el-tag :type="row.group_type==='fixed'?'info':'success'" size="small">{{ row.group_type==='fixed'?'VM':'容器' }}</el-tag></template>
        </el-table-column>
        <!-- 核心载体: fixed展示包名/artifact_id, elastic展示镜像 -->
        <el-table-column label="核心载体" width="160" show-overflow-tooltip>
          <template #default="{row}">
            <span v-if="row.group_type==='fixed'">{{ row.artifact_file_name || '-' }} {{ row.artifact_id ? '('+row.artifact_id+')' : '' }}</span>
            <span v-else>{{ row.image_repo ? row.image_repo+'/' : '' }}{{ row.image_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="jvm_opts" label="JVM参数" width="140" show-overflow-tooltip />
        <el-table-column prop="lock_status" label="发布锁" width="90">
          <template #default="{row}">
            <el-tag :type="row.lock_status===1?'danger':'success'" size="small">
              {{ row.lock_status===1?'🔴 发布中':'空闲' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{row}">
            <el-button size="small" type="primary" link @click="$router.push('/instance?group_id='+row.id)">下钻</el-button>
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="doRemove(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" v-model:current-page="page" :total="total" :page-size="size" @current-change="fetch" layout="total,prev,pager,next" />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog :title="form.id?'编辑部署分组':'新增部署分组'" v-model="visible" width="950px">
      <el-form :model="form" label-width="140px">
        <!-- === 通用字段 === -->
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="环境" required>
              <el-select v-model="form.env_code" style="width:100%" filterable>
                <el-option v-for="e in envOptions" :key="e.env_code" :label="e.env_code" :value="e.env_code" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="应用" required>
              <el-select v-model="form.app_code" style="width:100%" filterable>
                <el-option v-for="a in appOptions" :key="a.app_code" :label="a.app_code+' - '+a.app_name" :value="a.app_code" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="集群ID" required>
              <el-select v-model="form.cluster_id" style="width:100%" filterable>
                <el-option v-for="c in clusterOptions" :key="c.id" :label="c.cluster_code+' - '+c.cluster_name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="分组编码" required><el-input v-model="form.group_code" placeholder="default-group" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="分组名称" required><el-input v-model="form.group_name" placeholder="默认分组" /></el-form-item></el-col>
          <el-col :span="8">
            <el-form-item label="分组类型">
              <el-select v-model="form.group_type" style="width:100%">
                <el-option value="fixed" label="固定主机(fixed)" />
                <el-option value="elastic" label="弹性容器(elastic)" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="发布账号"><el-input v-model="form.deploy_user" placeholder="appdeploy" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="部署策略"><el-select v-model="form.deploy_strategy" style="width:100%"><el-option value="full" label="全量" /><el-option value="incr" label="增量" /></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="包类型"><el-select v-model="form.package_type" style="width:100%"><el-option value="jar" /><el-option value="war" /><el-option value="tar" /></el-select></el-form-item></el-col>
        </el-row>
        <el-form-item label="健康检查地址"><el-input v-model="form.health_check_url" placeholder="http://127.0.0.1:8080/health" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="启动脚本"><el-input v-model="form.start_script" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="停止脚本"><el-input v-model="form.stop_script" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="中间件域"><el-input v-model="form.middleware_domain" placeholder="middleware.bank.com" /></el-form-item>

        <!-- === 分支1: fixed (虚拟机) === -->
        <template v-if="form.group_type==='fixed'">
          <el-divider content-position="left">虚拟机部署配置</el-divider>
          <el-row :gutter="16">
            <el-col :span="8"><el-form-item label="固定包名"><el-input v-model="form.artifact_file_name" placeholder="biz.tar / app.war" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="artifact_id"><el-input v-model="form.artifact_id" placeholder="TSF CVM包唯一ID" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="解压部署"><el-switch v-model="form.unpack_flag" active-value="Y" inactive-value="N" /></el-form-item></el-col>
          </el-row>
          <el-form-item label="JVM参数"><el-input v-model="form.jvm_opts" type="textarea" :rows="2" placeholder="-Xms2g -Xmx4g" /></el-form-item>
          <el-row :gutter="16">
            <el-col :span="12"><el-form-item label="部署路径"><el-input v-model="form.deploy_path" placeholder="/data/app/loan-core" /></el-form-item></el-col>
          </el-row>
          <p style="color:#909399;font-size:12px">💡 传统VM差异化的启停/路径，请前往主机实例页面维护</p>
        </template>

        <!-- === 分支2: elastic (容器) === -->
        <template v-if="form.group_type==='elastic'">
          <el-divider content-position="left">容器镜像配置</el-divider>
          <el-row :gutter="16">
            <el-col :span="8"><el-form-item label="镜像仓库"><el-input v-model="form.image_repo" placeholder="registry.bank.com/library" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="镜像名称" required><el-input v-model="form.image_name" placeholder="loan-core" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="镜像Tag"><el-input value="latest" placeholder="latest（存量复用字段）" /></el-form-item></el-col>
          </el-row>
          <!-- container_platform=tsf 才展示TSF部署组ID -->
          <el-form-item v-if="selectedClusterPlatform==='tsf'" label="TSF部署组ID"><el-input v-model="form.deploy_group_id" placeholder="TSF平台部署组ID" /></el-form-item>
          <el-divider content-position="left">容器资源配额</el-divider>
          <el-row :gutter="16">
            <el-col :span="8"><el-form-item label="CPU Request"><el-input v-model="form.cpu_request" placeholder="500m" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="CPU Limit"><el-input v-model="form.cpu_limit" placeholder="2000m" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="副本数"><el-input v-model="form.replicas" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="8"><el-form-item label="Memory Request"><el-input v-model="form.mem_request" placeholder="512Mi" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="Memory Limit"><el-input v-model="form.mem_limit" placeholder="2048Mi" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="灰度权重"><el-input v-model="form.tsf_traffic_weight" placeholder="0" /></el-form-item></el-col>
          </el-row>
          <el-form-item label="更新策略"><el-radio-group v-model="form.update_type"><el-radio :value="0">立即更新</el-radio><el-radio :value="1">滚动更新</el-radio></el-radio-group></el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" @click="doSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { groupApi, envApi, appApi, clusterApi } from '../api'
import { useRoute } from 'vue-router'

const route = useRoute()
const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const size = 20
const visible = ref(false)
const envOptions = ref([])
const appOptions = ref([])
const clusterOptions = ref([])
const filterEnv = ref(route.query.env_code || '')
const filterApp = ref(route.query.app_code || '')
const filterCluster = ref(route.query.cluster_id || '')
const filterGroupType = ref('')
const filterLock = ref('')

const emptyForm = () => ({
  env_code: '', app_code: '', cluster_id: 0, group_code: 'default-group', group_name: '默认分组',
  group_type: 'fixed', status: 1, deploy_group_id: '', package_type: '',
  artifact_file_name: '', deploy_path: '', deploy_user: '', deploy_strategy: 'full', unpack_flag: 'Y',
  jvm_opts: '', health_check_url: '', start_script: '', stop_script: '',
  image_repo: '', image_name: '', artifact_id: '',
  cpu_request: '', cpu_limit: '', mem_request: '', mem_limit: '',
  replicas: 0, tsf_traffic_weight: 0, update_type: 0,
  middleware_domain: '', middleware_cluster_name: '', admin_url: '',
})
const form = reactive(emptyForm())

// 从集群列表读取当前选中集群的 container_platform
const selectedClusterPlatform = computed(() => {
  if (!form.cluster_id) return ''
  const c = clusterOptions.value.find(x => x.id === Number(form.cluster_id))
  return c?.container_platform || ''
})

// group_type=elastic 切换时预填充一些容器默认值
watch(() => form.group_type, (v) => {
  if (v === 'fixed') {
    form.image_repo = ''; form.image_name = ''; form.artifact_id = ''
  }
})

function rowClass({ row }) {
  return row.lock_status === 1 ? 'warning-row' : ''
}

function openDialog(row) {
  Object.assign(form, row ? { ...row, status: row.status || 1 } : emptyForm())
  visible.value = true
}

async function fetchOptions() {
  envOptions.value = await envApi.all() || []
  const appR = await appApi.list({ size: 1000 })
  appOptions.value = appR.items || []
  const clusterR = await clusterApi.list({ page: 1, size: 1000 })
  clusterOptions.value = clusterR.items || []
}

async function fetch() {
  loading.value = true
  const all = await groupApi.list({ page: 1, size: 1000 })
  let data = all.items || []
  if (filterEnv.value) data = data.filter(i => i.env_code === filterEnv.value)
  if (filterApp.value) data = data.filter(i => i.app_code === filterApp.value)
  if (filterCluster.value) data = data.filter(i => String(i.cluster_id) === String(filterCluster.value))
  if (filterGroupType.value) data = data.filter(i => i.group_type === filterGroupType.value)
  if (filterLock.value === '1') data = data.filter(i => i.lock_status === 1)
  else if (filterLock.value === '0') data = data.filter(i => i.lock_status !== 1)
  const start = (page.value - 1) * size
  tableData.value = data.slice(start, start + size)
  total.value = data.length
  loading.value = false
}

async function doSave() {
  form.cluster_id = Number(form.cluster_id) || 0
  form.status = Number(form.status)
  form.replicas = Number(form.replicas) || 0
  form.tsf_traffic_weight = Number(form.tsf_traffic_weight) || 0
  form.update_type = Number(form.update_type)
  await groupApi.save(form)
  ElMessage.success('保存成功')
  visible.value = false
  fetch()
}

async function doRemove(id) {
  await groupApi.remove(id)
  ElMessage.success('已删除')
  fetch()
}

onMounted(() => { fetchOptions(); fetch() })
</script>

<style>
.el-table .warning-row { background-color: #fef0f0 !important; }
</style>
