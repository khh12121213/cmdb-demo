<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>应用管理</span>
          <el-button type="primary" @click="openDialog()">新增应用</el-button>
        </div>
      </template>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="sys_id" label="系统ID" width="80" />
        <el-table-column prop="app_code" label="应用编码" width="140" />
        <el-table-column prop="app_name" label="应用名称" width="160" />
        <el-table-column prop="app_type" label="类型" width="120" />
        <el-table-column prop="owner" label="负责人" width="100" />
        <el-table-column prop="dev_owner" label="研发负责人" width="110" />
        <el-table-column prop="ops_owner" label="运维负责人" width="110" />
        <el-table-column prop="server_port" label="端口" width="80" />
        <el-table-column prop="base_jvm_opts" label="JVM参数" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="180">
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

    <el-dialog :title="form.id?'编辑应用':'新增应用'" v-model="visible" width="700px">
      <el-form :model="form" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="归属系统" required><el-select v-model="form.sys_id" style="width:100%" filterable><el-option v-for="s in sysOptions" :key="s.id" :label="s.sys_code + ' - ' + s.sys_name" :value="s.id" /></el-select></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="应用编码" required><el-input v-model="form.app_code" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="应用名称" required><el-input v-model="form.app_name" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-select v-model="form.app_type" style="width:100%">
                <el-option v-for="t in appTypes" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="负责人"><el-input v-model="form.owner" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="研发负责人"><el-input v-model="form.dev_owner" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="运维负责人"><el-input v-model="form.ops_owner" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="服务端口"><el-input v-model="form.server_port" placeholder="8080" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="监控端口"><el-input v-model="form.management_port" placeholder="8081" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="蓝鲸业务ID"><el-input v-model="form.default_bk_biz_id" placeholder="200" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="进程名"><el-input v-model="form.proc_name" /></el-form-item>
        <el-form-item label="代码仓库"><el-input v-model="form.repo_url" /></el-form-item>
        <el-form-item label="制品库"><el-input v-model="form.artifact_repo" /></el-form-item>
        <el-form-item label="JVM参数"><el-input v-model="form.base_jvm_opts" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="日志目录"><el-input v-model="form.log_base_dir" /></el-form-item>
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
import { appApi, sysApi } from '../api'

const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const size = 20
const visible = ref(false)
const sysOptions = ref([])
const form = reactive({ app_code: '', app_name: '', app_type: 'springboot', sys_id: 0, server_port: 8080, management_port: '', default_bk_biz_id: '', repo_url: '', artifact_repo: '', owner: '', dev_owner: '', ops_owner: '', proc_name: '', base_jvm_opts: '', log_base_dir: '' })
const appTypes = ['springboot', 'nginx', 'tongweb', 'weblogic', 'tsf-service']

function openDialog(row) {
  Object.assign(form, row ? { ...row } : { app_code: '', app_name: '', app_type: 'springboot', sys_id: 0, server_port: 8080, management_port: '', default_bk_biz_id: '', repo_url: '', artifact_repo: '', owner: '', dev_owner: '', ops_owner: '', proc_name: '', base_jvm_opts: '', log_base_dir: '' })
  visible.value = true
}

async function fetchSys() {
  const r = await sysApi.list({ size: 1000 })
  sysOptions.value = r.items
}

async function fetch() {
  loading.value = true
  const res = await appApi.list({ page: page.value, size })
  tableData.value = res.items
  total.value = res.total
  loading.value = false
}

async function doSave() {
  form.sys_id = Number(form.sys_id) || 0
  form.server_port = Number(form.server_port) || 0
  form.management_port = Number(form.management_port) || 0
  form.default_bk_biz_id = Number(form.default_bk_biz_id) || 0
  await appApi.save(form)
  ElMessage.success('保存成功')
  visible.value = false
  fetch()
}

async function doRemove(id) {
  await appApi.remove(id)
  ElMessage.success('已删除')
  fetch()
}

onMounted(() => { fetch(); fetchSys() })
</script>
