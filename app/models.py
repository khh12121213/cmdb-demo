import datetime
from sqlalchemy import (
    Column, BigInteger, Integer, String, Text, DateTime, Boolean,
    JSON, Index, text
)
from app.database import Base


class EnvInfo(Base):
    __tablename__ = "env_info"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    env_code = Column(String(32), nullable=False, comment="环境编码 dev/test/staging/prod")
    env_name = Column(String(64), nullable=False, comment="环境名称")
    env_tags = Column(String(255), default="", comment="权限标签")
    is_deleted = Column(Integer, default=0, comment="0正常 1删除")


class AppInfo(Base):
    __tablename__ = "app_info"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    app_code = Column(String(64), nullable=False, comment="应用唯一编码")
    sys_id = Column(BigInteger, default=0, comment="归属系统ID")
    app_name = Column(String(128), nullable=False, comment="应用名称")
    app_type = Column(String(32), nullable=False, comment="类型: springboot/nginx/tongweb/weblogic/tsf-service/docker/bes/websphere/tomcat/mysql/redis/kafka/es/mongodb/zookeeper/other")
    repo_url = Column(String(255), default="")
    artifact_repo = Column(String(255), default="")
    owner = Column(String(64), default="", comment="应用负责人")
    dev_owner = Column(String(64), default="", comment="研发负责人")
    ops_owner = Column(String(64), default="", comment="运维负责人")
    server_port = Column(Integer, default=0)
    management_port = Column(Integer, default=0)
    proc_name = Column(String(128), default="")
    base_jvm_opts = Column(String(1024), default="")
    log_base_dir = Column(String(255), default="")
    default_bk_biz_id = Column(BigInteger, default=0, comment="默认蓝鲸业务ID")
    is_deleted = Column(Integer, default=0)


class SysInfo(Base):
    __tablename__ = "sys_info"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    sys_code = Column(String(64), nullable=False, comment="系统唯一编码")
    sys_name = Column(String(128), nullable=False, comment="系统名称")
    dev_owner = Column(String(64), default="", comment="研发负责人")
    ops_owner = Column(String(64), default="", comment="运维负责人")
    remark = Column(String(255), default="", comment="备注")
    is_deleted = Column(Integer, default=0, comment="0正常 1删除")


class AppCluster(Base):
    __tablename__ = "app_cluster"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    env_code = Column(String(32), nullable=False)
    app_code = Column(String(64), nullable=False)
    cluster_code = Column(String(64), nullable=False, comment="集群唯一编码")
    cluster_name = Column(String(128), nullable=False)
    deploy_mode = Column(String(32), nullable=False, comment="fixed固定主机 | elastic弹性容器")
    tsf_cluster_id = Column(String(128), default="")
    namespace = Column(String(64), default="")
    labels = Column(String(512), default="", comment="灰度发布标签")
    status = Column(Integer, default=1, comment="1允许发布 0禁用投产")
    is_deleted = Column(Integer, default=0)


class AppDeployGroup(Base):
    __tablename__ = "app_deploy_group"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    env_code = Column(String(32), nullable=False)
    app_code = Column(String(64), nullable=False)
    cluster_id = Column(BigInteger, nullable=False)
    group_code = Column(String(64), nullable=False, comment="分组编码")
    group_name = Column(String(128), nullable=False)
    deploy_group_id = Column(String(128), default="", comment="TSF平台部署组ID")
    group_type = Column(String(16), nullable=False, comment="fixed / elastic")
    status = Column(Integer, default=1)

    # 虚拟机流水线核心字段
    artifact_file_name = Column(String(128), default="", comment="服务器固定包名")
    deploy_path = Column(String(255), default="", comment="应用部署根目录")
    deploy_user = Column(String(64), default="", comment="发布执行账号(加密)")
    deploy_strategy = Column(String(16), default="full", comment="full全量 | incr增量")
    unpack_flag = Column(String(1), default="Y", comment="Y解压 N不解压")
    jvm_opts = Column(String(1024), default="")
    health_check_url = Column(String(255), default="")
    start_script = Column(String(512), default="")
    stop_script = Column(String(512), default="")

    # TSF弹性容器字段
    cpu_request = Column(String(32), default="")
    cpu_limit = Column(String(32), default="")
    mem_request = Column(String(32), default="")
    mem_limit = Column(String(32), default="")
    replicas = Column(Integer, default=0)
    tsf_traffic_weight = Column(Integer, default=0)
    update_type = Column(Integer, default=0, comment="0立即更新 1滚动更新")

    # 传统中间件字段
    middleware_domain = Column(String(128), default="")
    middleware_cluster_name = Column(String(128), default="")
    admin_url = Column(String(255), default="")
    package_type = Column(String(32), default="", comment="jar/war/tar")

    # 发布并发锁
    lock_status = Column(Integer, default=0, comment="0空闲 1发布中")
    lock_trace_id = Column(String(128), default="")
    lock_expire_time = Column(DateTime, nullable=True)

    is_deleted = Column(Integer, default=0)


class ClusterInstance(Base):
    __tablename__ = "cluster_instance"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    deploy_group_id = Column(BigInteger, nullable=False)
    instance_ip = Column(String(39), default="")
    ssh_port = Column(Integer, default=22)

    # 蓝鲸五元组
    bk_biz_id = Column(BigInteger, default=0)
    bk_host_id = Column(BigInteger, default=0)
    bk_cloud_id = Column(Integer, default=0)
    bk_module_id = Column(BigInteger, default=0)
    bk_inner_ip = Column(String(39), default="")

    # 单机差异化配置
    deploy_user = Column(String(64), default="")
    deploy_path = Column(String(255), default="")
    instance_tags = Column(String(255), default="")
    instance_status = Column(Integer, default=1, comment="1正常 0维护禁用")
    start_script = Column(String(512), default="")
    stop_script = Column(String(512), default="")
    health_check_url = Column(String(255), default="")
    is_deleted = Column(Integer, default=0)


class CicdVariable(Base):
    __tablename__ = "cicd_variable"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    env_code = Column(String(32), nullable=False)
    app_code = Column(String(64), nullable=False)
    cluster_code = Column(String(64), default="")
    group_code = Column(String(64), default="")
    instance_id = Column(BigInteger, default=0)
    var_key = Column(String(128), nullable=False)
    var_value = Column(Text, comment="变量值")
    remark = Column(String(255), default="")
    is_deleted = Column(Integer, default=0)


class AppDeployGroupRelease(Base):
    __tablename__ = "app_deploy_group_release"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    env_code = Column(String(32), nullable=False)
    app_code = Column(String(64), nullable=False)
    cluster_id = Column(BigInteger, nullable=False)
    group_code = Column(String(64), nullable=False)
    build_no = Column(String(64), default="", comment="Jenkins构建编号")
    git_commit = Column(String(64), default="")
    artifact_version = Column(String(128), nullable=False, comment="投产版本备注")
    release_user = Column(String(64), nullable=False)
    release_time = Column(DateTime, default=datetime.datetime.utcnow)
    release_status = Column(String(16), nullable=False, comment="success/fail/rollback")
    is_current = Column(Integer, default=0, comment="1=当前生效基线")
    version = Column(BigInteger, default=0, comment="乐观锁版本号")
    remark = Column(String(500), default="")
    is_deleted = Column(Integer, default=0)


class ClusterInstanceRelease(Base):
    __tablename__ = "cluster_instance_release"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    instance_id = Column(BigInteger, nullable=False)
    cluster_release_id = Column(BigInteger, nullable=False, comment="关联基线记录ID")
    instance_ip = Column(String(39), default="")
    build_no = Column(String(64), nullable=False)
    current_version = Column(String(128), nullable=False)
    deploy_time = Column(DateTime, default=datetime.datetime.utcnow)
    deploy_result = Column(String(16), nullable=False, comment="success/fail")
    is_deleted = Column(Integer, default=0)


class SysAuditLog(Base):
    __tablename__ = "sys_audit_log"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    operator = Column(String(64), nullable=False)
    operation = Column(String(32), nullable=False, comment="INSERT/UPDATE/DELETE/PUBLISH/SYNC/SECRET_QUERY")
    target_table = Column(String(64), nullable=False)
    target_biz_key = Column(String(128), nullable=False)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    request_ip = Column(String(64), nullable=True)
    trace_id = Column(String(128), default="")
    create_time = Column(DateTime, default=datetime.datetime.utcnow)
