from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from scanner.models import TargetHost, PortInfo
from scanner import core
from scanner import utils
from ai.agent import NetworkSecurityAgent

import asyncio

"""
As it is not the scope of this project to make a very extensive website,
I only implement the very simple website - server logic.
However i had to make a websocket to integrate the chat logic between user and an AI.
"""

app = FastAPI(
    title = "Local Network Scanner API",
    description = ""
)

live_hosts = []  # Global variable to store live hosts data for AI analysis

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

    global live_hosts

    network_cidr = utils.get_network_cidr()

    scanner = core.CoreNetworkScanner(host_limit = 20, port_limit = 50, timeout = 1.0)

    await scanner.scan_network(network_cidr)

    live_hosts = await utils.get_live_hosts_from_arp(network_cidr)
    live_hosts = await scanner.scan_live_hosts(live_hosts, 1, 1000)
    live_hosts = await utils.get_local_name(live_hosts)

    for host in live_hosts:
        host.os = host.guess_os()
    return live_hosts

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    global live_hosts

    agent = NetworkSecurityAgent()

    try:
        while True:
            question = await websocket.receive_text()

            if not question:
                continue

            answer = await agent.analyze_query(question, live_hosts)

            await websocket.send_text(answer)
            
    except WebSocketDisconnect:
        pass
