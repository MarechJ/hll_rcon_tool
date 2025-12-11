from typing import TypedDict
import psutil


class CPU_Usage(TypedDict):
    cores: int
    percent: float
    process_count: int


class RAM_Usage(TypedDict):
    total: float
    used: float
    percent: float


class DISK_Usage(TypedDict):
    total: float
    used: float
    percent: float


class SystemUsage(TypedDict):
    cpu_usage: CPU_Usage
    ram_usage: RAM_Usage
    disk_usage: DISK_Usage


def get_cpu_usage(interval: float | None = None) -> CPU_Usage:
    cpu_percent = psutil.cpu_percent(interval=interval)
    process_count = len(list(psutil.process_iter()))
    return CPU_Usage(
        cores=psutil.cpu_count() or 0,
        percent=cpu_percent,
        process_count=process_count,
    )


def get_ram_usage() -> RAM_Usage:
    memory = psutil.virtual_memory()
    return RAM_Usage(
        total=memory.total / (1024**3),  # Convert to GB
        used=memory.used / (1024**3),
        percent=memory.percent,
    )


def get_disk_usage() -> DISK_Usage:
    disk = psutil.disk_usage("/")
    return DISK_Usage(
        total=disk.total / (1024**3),  # Convert to GB
        used=disk.used / (1024**3),
        percent=disk.percent,
    )


def get_system_usage(interval: float | None = None) -> SystemUsage:
    return SystemUsage(
        cpu_usage=get_cpu_usage(interval=interval),
        ram_usage=get_ram_usage(),
        disk_usage=get_disk_usage(),
    )
