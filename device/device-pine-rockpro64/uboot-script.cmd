setenv bootargs init=/init.sh rw console=tty0 console=ttyS0,115200 no_console_suspend panic=10 consoleblank=0 loglevel=1 cma=256M PMOS_NO_OUTPUT_REDIRECT

printenv

echo Loading DTB
load mmc ${mmc_bootdev}:1 ${fdt_addr_r} dtb-postmarketos-stable.dtb

echo Loading Initramfs
load mmc ${mmc_bootdev}:1 ${ramdisk_addr_r} uInitrd-postmarketos-stable

echo Loading Kernel
load mmc ${mmc_bootdev}:1 ${kernel_addr_r} vmlinuz-postmarketos-stable

echo Resizing FDT
fdt addr ${fdt_addr_r}
fdt resize

echo Booting kernel
booti ${kernel_addr_r} ${ramdisk_addr_r} ${fdt_addr_r}
