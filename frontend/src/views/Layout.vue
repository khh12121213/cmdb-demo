<template>
  <el-container style="height:100vh">
    <el-aside width="200px" style="background:#304156">
      <div style="padding:16px;text-align:center;color:#fff;font-size:18px;font-weight:bold">
        🏦 CMDB 管理端
      </div>
      <el-menu
        :default-active="$route.path"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        router
      >
        <el-menu-item index="/env"><el-icon><Setting /></el-icon> 环境管理</el-menu-item>
        <el-menu-item index="/app"><el-icon><Grid /></el-icon> 应用管理</el-menu-item>
        <el-menu-item index="/cluster"><el-icon><Connection /></el-icon> 集群管理</el-menu-item>
        <el-menu-item index="/group"><el-icon><Operation /></el-icon> 部署组管理</el-menu-item>
        <el-menu-item index="/instance"><el-icon><Monitor /></el-icon> 主机实例</el-menu-item>
        <el-menu-item index="/variable"><el-icon><Key /></el-icon> 变量配置</el-menu-item>
        <el-menu-item index="/release"><el-icon><Finished /></el-icon> 发布基线</el-menu-item>
        <el-menu-item index="/audit"><el-icon><Document /></el-icon> 审计日志</el-menu-item>
      </el-menu>
    </el-aside>
    <el-main style="background:#f0f2f5;padding:20px;overflow-y:auto">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
</script>
