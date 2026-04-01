from fastapi import FastAPI
from fastapi.responses import FileResponse

from scanner.models import TargetHost, PortInfo
from scanner import core
from scanner import utils

app = FastAPI(
    title = "Local Network Scanner API",
    description = ""
)

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.get("/scan.html")
async def read_scan():
    return FileResponse('frontend/scan.html')

@app.get("/results.html")
async def read_results():
    return FileResponse('frontend/results.html')

@app.get("/api/scan")
async def scan_network():

    network_cidr = utils.get_network_cidr()

    scanner = core.CoreNetworkScanner(host_limit = 20, port_limit = 50, timeout = 1.0)

    await scanner.scan_network(network_cidr)

    live_hosts = await utils.get_live_hosts_from_arp(network_cidr)
    live_hosts = await scanner.scan_live_hosts(live_hosts, 1, 1000)
    live_hosts = await utils.get_local_name(live_hosts)

    for host in live_hosts:
        host.os = host.guess_os()
    return live_hosts