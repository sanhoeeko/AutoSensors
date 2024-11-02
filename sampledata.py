free = """
              总计         已用        空闲      共享    缓冲/缓存    可用
内存：      128552        1234      123287           3        4030      126269
交换：      110785           0      110785
"""

top = """
top - 12:56:14 up 34 days, 16:53,  2 users,  load average: 0.06, 0.02, 0.00
任务: 1125 total,   1 running, 621 sleeping,   0 stopped,   0 zombie
KiB Mem : 13163808+total, 12624108+free,  1271444 used,  4125556 buff/cache
KiB Swap: 11344394+total, 11344394+free,        0 used. 12929291+avail Mem 

进程 USER      PR  NI    VIRT    RES    SHR   %CPU %MEM     TIME+ COMMAND
 27021 gengjie   20   0   46972   5084   3460 R  15.0  0.0   0:00.07 top
"""

sensors = """
coretemp-isa-0000
Adapter: ISA adapter
Package id 0:  +28.0°C  (high = +81.0°C, crit = +91.0°C)
Core 0:        +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 1:        +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 2:        +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 3:        +25.0°C  (high = +81.0°C, crit = +91.0°C)
Core 4:        +28.0°C  (high = +81.0°C, crit = +91.0°C)
Core 5:        +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 6:        +28.0°C  (high = +81.0°C, crit = +91.0°C)
Core 8:        +25.0°C  (high = +81.0°C, crit = +91.0°C)
Core 9:        +26.0°C  (high = +81.0°C, crit = +91.0°C)
Core 10:       +25.0°C  (high = +81.0°C, crit = +91.0°C)
Core 11:       +28.0°C  (high = +81.0°C, crit = +91.0°C)
Core 12:       +25.0°C  (high = +81.0°C, crit = +91.0°C)
Core 13:       +25.0°C  (high = +81.0°C, crit = +91.0°C)
Core 14:       +26.0°C  (high = +81.0°C, crit = +91.0°C)
Core 16:       +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 17:       +26.0°C  (high = +81.0°C, crit = +91.0°C)
Core 18:       +26.0°C  (high = +81.0°C, crit = +91.0°C)
Core 19:       +25.0°C  (high = +81.0°C, crit = +91.0°C)
Core 20:       +25.0°C  (high = +81.0°C, crit = +91.0°C)
Core 21:       +25.0°C  (high = +81.0°C, crit = +91.0°C)
Core 22:       +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 24:       +24.0°C  (high = +81.0°C, crit = +91.0°C)
Core 25:       +25.0°C  (high = +81.0°C, crit = +91.0°C)
Core 26:       +26.0°C  (high = +81.0°C, crit = +91.0°C)
Core 27:       +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 28:       +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 29:       +23.0°C  (high = +81.0°C, crit = +91.0°C)
Core 30:       +25.0°C  (high = +81.0°C, crit = +91.0°C)

amdgpu-pci-7300
Adapter: PCI adapter
vddgfx:       +0.78 V  
fan1:        2023 RPM  (min = 1800 RPM, max = 6000 RPM)
edge:         +33.0°C  (crit = +97.0°C, hyst = -273.1°C)
power1:        3.06 W  (cap =  25.00 W)

coretemp-isa-0001
Adapter: ISA adapter
Package id 1:  +33.0°C  (high = +81.0°C, crit = +91.0°C)
Core 0:        +29.0°C  (high = +81.0°C, crit = +91.0°C)
Core 1:        +30.0°C  (high = +81.0°C, crit = +91.0°C)
Core 2:        +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 3:        +28.0°C  (high = +81.0°C, crit = +91.0°C)
Core 4:        +29.0°C  (high = +81.0°C, crit = +91.0°C)
Core 5:        +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 6:        +30.0°C  (high = +81.0°C, crit = +91.0°C)
Core 8:        +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 9:        +28.0°C  (high = +81.0°C, crit = +91.0°C)
Core 10:       +29.0°C  (high = +81.0°C, crit = +91.0°C)
Core 11:       +29.0°C  (high = +81.0°C, crit = +91.0°C)
Core 12:       +29.0°C  (high = +81.0°C, crit = +91.0°C)
Core 13:       +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 14:       +26.0°C  (high = +81.0°C, crit = +91.0°C)
Core 16:       +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 17:       +26.0°C  (high = +81.0°C, crit = +91.0°C)
Core 18:       +26.0°C  (high = +81.0°C, crit = +91.0°C)
Core 19:       +28.0°C  (high = +81.0°C, crit = +91.0°C)
Core 20:       +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 21:       +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 22:       +28.0°C  (high = +81.0°C, crit = +91.0°C)
Core 24:       +26.0°C  (high = +81.0°C, crit = +91.0°C)
Core 25:       +26.0°C  (high = +81.0°C, crit = +91.0°C)
Core 26:       +28.0°C  (high = +81.0°C, crit = +91.0°C)
Core 27:       +29.0°C  (high = +81.0°C, crit = +91.0°C)
Core 28:       +26.0°C  (high = +81.0°C, crit = +91.0°C)
Core 29:       +27.0°C  (high = +81.0°C, crit = +91.0°C)
Core 30:       +27.0°C  (high = +81.0°C, crit = +91.0°C)

dell_smm-virtual-0
Adapter: Virtual device
fan1:           0 RPM
fan2:         320 RPM
fan3:         801 RPM
"""
