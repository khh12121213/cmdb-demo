<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>部署组管理</span>
          <el-button type="primary" @click="openDialog()">新增部署组</el-button>
        </div>
      </template>
      <div style="margin-bottom:12px;display:flex;gap:12px">
        <el-input v-model="filterEnv" placeholder="环境编码" clearable style="width:150px" @change="fetch" />
        <el-input v-model="filterApp" placeholder="应用编码" clearable style="width:150px" @change="fetch" />
      </div>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="env_code" label="环境" width="80" />
        <el-table-column prop="app_code" label="应用" width="110" />
        <el-table-column prop="group_code" label="分组编码" width="130" />
        <el-table-column prop="group_name" label="分组名称" width="120" />
        <el-table-column prop="group_type" label="类型" width="80" />
        <el-table-column prop="artifact_file_name" label="固定包名" width="120" />
        <el-table-column prop="deploy_strategy" label="策略" width="80" />
        <el-table-column prop="lock_status" label="发布锁" width="90">
          <template #default="{row}">
            <el-tag :type="row.lock_status===1?'danger':'success'" size="small">
              {{ row.lock_status===1?'发布中':'空闲' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{row}">
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

    <el-dialog :title="form.id?'编辑部署组':'新增部署组'" v-model="visible" width="900px">
      <el-form :model="form" label-width="130px">
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="环境" required><el-input v-model="form.env_code" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="应用" required><el-input v-model="form.app_code" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="集群ID" required><el-input v-model="form.cluster_id" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="分组编码" required><el-input v-model="form.group_code" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="分组名称" required><el-input v-model="form.group_name" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="类型"><el-select v-model="form.group_type" style="width:100%"><el-option value="fixed" label="固定主机"/><el-option value="elastic" label="弹性容器"/></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="状态"><el-switch v-model="form.status" :active-value="1" :inactive-value="0" /></el-form-item></el-col>
        </el-row>
        <el-divider content-position="left">虚拟机部署配置</el-divider>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="固定包名"><el-input v-model="form.artifact_file_name" placeholder="biz.tar" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="部署策略"><el-select v-model="form.deploy_strategy" style="width:100%"><el-option value="full" label="全量"/><el-option value="incr" label="增量"/></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="解压部署"><el-switch v-model="form.unpack_flag" active-value="Y" inactive-value="N" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="部署路径"><el-input v-model="form.deploy_path" placeholder="/data/app/loan-core" /></el-form-item>
        <el-form-item label="执行账号"><el-input v-model="form.deploy_user" placeholder="appdeploy（将加密存储）" /></el-form-item>
        <el-form-item label="健康检查"><el-input v-model="form.health_check_url" placeholder="http://127.0.0.1:8080/health" /></el-form-item>
        <el-form-item label="JVM参数"><el-input v-model="form.jvm_opts" type="textarea" :rows="2" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="启动脚本"><el-input v-model="form.start_script" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="停止脚本"><el-input v-model="form.stop_script" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" @click="doSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { groupApi } from '../api'

const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const size = 20
const visible = ref(false)
const emptyForm = () => ({ env_code: '', app_code: '', cluster_id: 0, group_code: 'default-group', group_name: '默认分组', group_type: 'fixed', status: 1, artifact_file_name: '', deploy_path: '', deploy_user: '', deploy_strategy: 'full', unpack_flag: 'Y', jvm_opts: '', health_check_url: '', start_script: '', stop_script: '' })
const form = reactive(emptyForm())
const filterEnv = ref('')
const filterApp = ref('')

function openDialog(row) {
  Object.assign(form, row ? { ...row, status: row.status || 1 } : emptyForm())
  visible.value = true
}

async function fetch() {
  loading.value = true
  const res = await groupApi.list({ page: page.value, size, env_code: filterEnv.value, app_code: filterApp.value })
  tableData.value = res.items
  total.value = res.total
  loading.value = false
}

async function doSave() {
  form.cluster_id = Number(form.cluster_id) || 0
  form.status = Number(form.status)
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

onMounted(fetch)
</script>
