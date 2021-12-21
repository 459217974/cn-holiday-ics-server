# cn-holiday-ics-server
A calendar subscribe server

## 直接使用我搭建的服务

* 订阅节假日：https://cdxy.fun:9999/holiday
* 订阅调休上班：https://cdxy.fun:9999/workday
* 节假日和调休上班在一起的版本：https://cdxy.fun:9999/holiday_and_workday

## 部署自己的服务

```
bash
git clone git@github.com:459217974/cn-holiday-ics-server.git
git submodule update --init
docker build . -t cn-holiday-ics-server
docker run -d -p {export_port}:8080 -v {store_data_path}:/usr/src/app/data --name cn-holiday-ics-server cn-holiday-ics-server
```

包括项目的一些其他信息，后续有时间再补充。
