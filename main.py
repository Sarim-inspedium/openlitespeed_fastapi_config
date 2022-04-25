from fastapi import FastAPI
import db4u

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/db4u_install")
async def db4u_install():
    return {"message": db4u.db4u()}

@app.get("/vhost_create/{domain_name}")
async def read_item(domain_name):
    user=db4u.vhost(domain_name)
    return {"user": user[0], "password":user[1]}


@app.get("/service_status/{service}")
async def s_status(service):
    value = db4u.service_status(service)
    if value ==0:
        return {"message": service+" is running ", "Status":True}
    else:
        return {"message": service+" is not running ", "Status":False}

@app.get("/service_stop/{service}")
async def s_stop(service):
    value = db4u.service_stop(service)
    return {"message": service+" has stoped"}

@app.get("/service_restart/{service}")
async def s_restart(service):
    value = db4u.service_restart(service)
    return {"message": service+" has restarted"}

@app.get("/add_ssl/{domian}")
async def add_ssl(domian):
    return {"message": db4u.add_ssl(domian)}
