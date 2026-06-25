@echo off
echo Testing pinggy
ssh -p 443 -R0:localhost:8000 a.pinggy.io > ssh_out.txt 2>&1
