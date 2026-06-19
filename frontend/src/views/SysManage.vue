<template>
  <div>
    <el-card>
      <template #header>系统管理</template>
      <el-row :gutter="12">
        <el-col :span="4"><el-button type="primary" @click="openAdd">新增系统</el-button></el-col>
      </el-row>
      <el-table :data="items" style="margin-top:12px">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="sys_code" label="系统编码" width="130" />
        <el-table-column prop="sys_name" label="系统名称" />
        <el-table-column prop="dev_owner" label="研发负责人" width="120" />
        <el-table-column prop="ops_owner" label="运维负责人" width="120" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="160">
          <template #default="{row}">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="doRemove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" v-model:current-page="page" :total="total" :page-size="size" @current-change="fetch" layout="total,prev,pager,next" />
    </el-card>

    <el-dialog :title="form.id?'编辑系统':'新增系统'" v-model="visible" width="600px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="系统编码" required><el-input v-model="form.sys_code" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="系统名称" required><el-input v-model="form.sys_name" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="研发负责人"><el-input v-model="form.dev_owner" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="运维负责人"><el-input v-model="form.ops_owner" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="form.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="visible=false">取消</el-button><el-button type="primary" @click="doSave">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { sysApi } from '../api'

const items = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(20)
const visible = ref(false)

const emptyForm = () => ({ id: 0, sys_code: '', sys_name: '', dev_owner: '', ops_owner: '', remark: '' })
const form = reactive(emptyForm())

async function fetch() {
  const r = await sysApi.list({ page: page.value, size: size.value })
  items.value = r.items; total.value = r.total
}

function openAdd() { Object.assign(form, emptyForm()); visible.value = true }
function openEdit(row) { Object.assign(form, row); visible.value = true }

async function doSave() {
  await sysApi.save(form)
  visible.value = false; fetch()
}

async function doRemove(id) {
  await sysApi.remove(id)
  fetch()
}

fetch()
</script>
