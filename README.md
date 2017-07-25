# alert_python_script_api
操作influxdb进行监控告警，使用告警平台api脚本

- 脚本放置目录：

      /data/influxdb_python
       
       
- 目录结构如下：

      /data/influxdb_python
    
      /data/influxdb_python/cpu_alert.py   cpu告警脚本
    
      /data/influxdb_python/mem_alert.py   mem告警脚本
    
      /data/influxdb_python/log/           定时任务执行日志
    
      /data/influxdb_python/output/         临时输出异常主机信息目录
      
- 定时任务配置：(默认两分钟执行一次)

      */2 * * * * python /data/influxdb_python/cpu_alert.py
    
      */2 * * * * python /data/influxdb_python/mem_alert.py
