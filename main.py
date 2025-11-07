#!/usr/bin/env python3
import sys
import time
import os
import platform
import importlib
from datetime import datetime
print(r"""
░██╗░░░░░░░██╗░██████╗██╗  ████████╗░█████╗░░█████╗░██╗░░░░░
░██║░░██╗░░██║██╔════╝██║  ╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░
░╚██╗████╗██╔╝╚█████╗░██║  ░░░██║░░░██║░░██║██║░░██║██║░░░░░
░░████╔═████║░░╚═══██╗██║  ░░░██║░░░██║░░██║██║░░██║██║░░░░░
░░╚██╔╝░╚██╔╝░██████╔╝██║  ░░░██║░░░╚█████╔╝╚█████╔╝███████╗
░░░╚═╝░░░╚═╝░░╚═════╝░╚═╝  ░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝
""")
print('\nWindows System Inspector — Detailed (Console)\n')
optional = {}
def try_import(name, pkg=None):
    try:
        m = importlib.import_module(name)
        optional[name] = True
        return m
    except Exception:
        optional[name] = False
        return None

psutil = try_import('psutil')
GPUtil = try_import('GPUtil')
cpuinfo = try_import('cpuinfo')
wmi = try_import('wmi')

def line():
    print('-' * 80)

line()
print('Timestamp:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
line()
print('SYSTEM OVERVIEW')
print('Platform:', platform.system(), platform.release(), platform.version())
print('Machine:', platform.machine())
print('Processor (platform):', platform.processor())
try:
    print('Python:', sys.version.replace('\n', ' '))
except Exception:
    pass
if psutil:
    try:
        boot = datetime.fromtimestamp(psutil.boot_time())
        uptime_s = time.time() - psutil.boot_time()
        print('System boot time:', boot.strftime('%Y-%m-%d %H:%M:%S'))
        print('Uptime (seconds):', int(uptime_s))
    except Exception:
        pass
else:
    print('psutil not available: limited runtime info')
line()
print('CPU')
if cpuinfo:
    try:
        info = cpuinfo.get_cpu_info()
        print('Brand:', info.get('brand_raw'))
        print('Arch:', info.get('arch'))
        print('Bits:', info.get('bits'))
        print('Hz advertised:', info.get('hz_advertised_friendly'))
    except Exception:
        pass
if psutil:
    try:
        print('Physical cores:', psutil.cpu_count(logical=False))
        print('Logical cores:', psutil.cpu_count(logical=True))
        freq = psutil.cpu_freq()
        if freq:
            print('Max freq (MHz):', getattr(freq, 'max', None))
            print('Current freq (MHz):', getattr(freq, 'current', None))
        print('CPU percent (1s sample):', psutil.cpu_percent(interval=1))
    except Exception:
        pass
else:
    print('psutil not available: limited CPU info')
line()
print('MEMORY')
if psutil:
    try:
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
        print('Total RAM (bytes):', vm.total)
        print('Available RAM (bytes):', vm.available)
        print('Used RAM (bytes):', vm.used)
        print('RAM percent:', vm.percent)
        print('Swap total (bytes):', sm.total)
        print('Swap used (bytes):', sm.used)
        print('Swap percent:', sm.percent)
    except Exception:
        pass
else:
    print('psutil not available: limited memory info')
line()
print('DISKS')
if psutil:
    try:
        for p in psutil.disk_partitions(all=False):
            try:
                u = psutil.disk_usage(p.mountpoint)
                print(f"Mountpoint: {p.device} -> {p.mountpoint} ({p.fstype})")
                print('  Total:', u.total, 'Used:', u.used, 'Free:', u.free, 'Percent:', u.percent)
            except Exception:
                print(f"  {p.device} ({p.fstype}) - access error")
        dio = psutil.disk_io_counters()
        if dio:
            print('Disk IO - read bytes:', dio.read_bytes, 'write bytes:', dio.write_bytes)
    except Exception:
        pass
else:
    print('psutil not available: limited disk info')
line()
print('GPU')
if GPUtil:
    try:
        gpus = GPUtil.getGPUs()
        for i,g in enumerate(gpus):
            print('GPU', i)
            print('  name:', g.name)
            print('  id:', g.id)
            print('  load:', g.load)
            print('  memoryTotal(MB):', g.memoryTotal)
            print('  memoryUsed(MB):', g.memoryUsed)
            print('  temperature (C):', g.temperature)
    except Exception:
        pass
else:
    print('GPUtil not available or no GPU detected')
line()
print('NETWORK')
if psutil:
    try:
        addrs = psutil.net_if_addrs()
        for iface, adds in addrs.items():
            print('Interface:', iface)
            for a in adds:
                print(' ', getattr(a, 'family', ''), getattr(a, 'address', ''), getattr(a, 'netmask', ''))
        nic = psutil.net_io_counters(pernic=False)
        if nic:
            print('Bytes sent:', nic.bytes_sent, 'Bytes recv:', nic.bytes_recv)
        cons = psutil.net_connections()
        print('Open connections count:', len(cons))
    except Exception:
        pass
else:
    print('psutil not available: limited network info')
line()
print('USERS & SESSIONS')
if psutil:
    try:
        for u in psutil.users():
            print('User:', u.name, 'Terminal:', getattr(u, 'terminal', None), 'Host:', getattr(u, 'host', None), 'Started:', datetime.fromtimestamp(u.started).strftime('%Y-%m-%d %H:%M:%S'))
    except Exception:
        pass
else:
    print('psutil not available: limited user/session info')
line()
print('TOP PROCESSES (by memory and CPU)')
if psutil:
    try:
        procs = []
        for p in psutil.process_iter(['pid','name','username','cpu_percent','memory_info']):
            try:
                p.info['cpu_percent'] = p.cpu_percent(interval=0.1)
                procs.append(p.info)
            except Exception:
                pass
        top_mem = sorted(procs, key=lambda x: getattr(x.get('memory_info') or {}, 'rss', 0), reverse=True)[:10]
        top_cpu = sorted(procs, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:10]
        print('Top memory consumers:')
        for p in top_mem:
            mem = getattr(p.get('memory_info') or {}, 'rss', 0)
            print(p.get('pid'), p.get('name'), 'user=', p.get('username'), 'mem_rss=', mem)
        print('Top CPU consumers:')
        for p in top_cpu:
            print(p.get('pid'), p.get('name'), 'user=', p.get('username'), 'cpu%=', p.get('cpu_percent'))
    except Exception:
        pass
else:
    print('psutil not available: limited process info')
line()
print('SERVICES & INSTALLED SOFTWARE (Windows-specific)')
if wmi:
    try:
        c = wmi.WMI()
        try:
            for s in c.Win32_Service():
                print('Service:', s.Name, 'State:', s.State, 'StartMode:', s.StartMode)
        except Exception:
            pass
        try:
            count = 0
            for p in c.Win32_Product():
                print('Installed:', p.Name, 'Version:', p.Version)
                count += 1
                if count > 50:
                    print('...more installed products omitted')
                    break
        except Exception:
            pass
    except Exception:
        pass
else:
    print('wmi not available: services/installed software listing limited')
line()
print('BIOS & MOTHERBOARD')
if wmi:
    try:
        c = wmi.WMI()
        for b in c.Win32_BIOS():
            print('BIOS Manufacturer:', b.Manufacturer, 'SMBIOSBIOSVersion:', getattr(b, 'SMBIOSBIOSVersion', None))
        for mb in c.Win32_BaseBoard():
            print('BaseBoard Manufacturer:', mb.Manufacturer, 'Product:', getattr(mb, 'Product', None))
    except Exception:
        pass
else:
    print('wmi not available: limited BIOS/motherboard info')
line()
print('SENSORS (temps, fans)')
if psutil:
    try:
        temps = getattr(psutil, 'sensors_temperatures', lambda: {})()
        if temps:
            for k,v in temps.items():
                print('Sensor:', k)
                for entry in v:
                    print(' ', entry.label, entry.current, entry.high, entry.critical)
        else:
            print('No sensors data from psutil')
    except Exception:
        pass
else:
    print('psutil not available: sensors not accessible')
line()
print('ENVIRONMENT & CONFIG')
try:
    print('Computer name:', os.environ.get('COMPUTERNAME'))
    print('User:', os.environ.get('USERNAME'))
    print('System drive:', os.environ.get('SystemDrive'))
    print('Path entries count:', len(os.environ.get('PATH','').split(';')))
except Exception:
    pass
line()
print('SUMMARY OF OPTIONAL MODULES (features that may be limited)')
for k,v in optional.items():
    print(k, 'available' if v else 'missing')
line()
print('End of report')
