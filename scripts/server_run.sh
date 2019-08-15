#!/usr/bin/env bash

BASEPATH="/data/apps/publish/scripts"
VIRTUALENV="/data/apps/publish/venv"

cd ${BASEPATH%scripts}

function uwsgi_start() {
   echo "start uwsgi........."
   ${VIRTUALENV}/bin/uwsgi --ini ${BASEPATH}/uwsgi_http.ini
}

function uwsgi_stop(){
  $(ps aux | grep "uwsgi" | awk '{print $2}' | xargs kill -9  2>/dev/null)
  if [[ $? -eq 0 ]];then
      echo "uwsgi stop OK........."
  fi
}

function ws_start() {
    echo "start websocket........."
    ${VIRTUALENV}/bin/daphne -b 0.0.0.0 -p 8001 publish.asgi:application 2>> ${BASEPATH}/ws.log&
}

function ws_stop() {
    $(ps aux | grep "daphne" | awk '{print $2}' | xargs kill -9 2>/dev/null)
    if [[ $? -eq 0 ]];then
      echo "websocket stop OK........."
    fi
}

function celery_start() {
    echo "start celery........."
    ${VIRTUALENV}/bin/celery worker -A publish -E -l info -f ${BASEPATH}/worker.log&
}

function celery_stop() {
    $(ps aux | grep "celery" | awk '{print $2}' | xargs kill -9 2>/dev/null)
    if [[ $? -eq 0 ]];then
      echo "celery stop OK........."
    fi
}

function Useage(){
     echo "$0 start/stop"
}

case $1 in
  start)
     uwsgi_start
     ws_start
     celery_start
   ;;
   stop)
      uwsgi_stop
      ws_stop
      celery_stop
   ;;
   *)
      Useage
    ;;
esac
