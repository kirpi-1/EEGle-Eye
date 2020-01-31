from celery import Celery
import urllib.request
import os
import visdom

BASEDIR = "~/code"

app = Celery('visdomApp', backend="rpc://", broker = "pyampq://ubuntu@10.0.0.12//")

vis = visdom.Visdom()

@app.task
def printer
