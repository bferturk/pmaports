This is a temporary file that should not end up in master!
---

We don't have working service files for everything yet. So below are the full commands required to start Anbox manually:

1. Start the container-manager (this now happens automatically using a service file)

```
# modprobe loop
# anbox container-manager --daemon --privileged --data-path=/var/lib/anbox # (command prints out nothing and waits, open another shell)
```

2. Hack to make the fifo work. For some reason, lxc is trying to access this file, which does not exist: `/run/lxc//var/lib/anbox/containers/monitor-fifo`

```
# mkdir -p /run/lxc
# ln -s /var /run/lxc/var
# mkfifo /var/lib/anbox/containers/monitor-fifo
```

3. Start session manager:

```
# export XDG_RUNTIME_DIR=/tmp/xdg
# mkdir -p "$XDG_RUNTIME_DIR"
# chmod 0700 "$XDG_RUNTIME_DIR"
# export DISPLAY=:0
# anbox session-manager
```

4. Run an Android app

```
$ export DISPLAY=:0
$ anbox launch --package=org.anbox.appmgr --component=org.anbox.appmgr.AppViewActivity
```

5. Logs
/var/lib/anbox/logs/container.log


Current fatal error in step 4:
lxc_cgfs - cgroups/cgfs.c:cgfs_init:2363 - cgroupfs failed to detect cgroup metadata

NOTE: one way to make LXC print more information is:
- extracting the lxc source
- edit the code to add more debug messages
- pmbootstrap build lxc --src=path/to/lxc
- (the path to the fifo was found that way)


TODO
- make both daemons work
- write openrc init scripts for the daemons
- add bridge (that's only needed to get internet in anbox, right?)
- "anbox version" says that git is missing ;)
- make sure that kernels where we want to use anbox have:
	ashmem, binder, squashfs_xz
	(possibly add to kconfig_check? "kconfig_check --anbox"?)
	(right now, squashfs_xz is only enabled for x86_64)
- clean up

