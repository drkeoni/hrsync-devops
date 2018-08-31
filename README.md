## hrsync-devops

This repository provides the devops magic for automating the deployment and
monitoring of the `hrsync` application.

### To install

```
make create-ve
make setup
```

### To manage hrsync

Start the EC2 instance:
```
lfab launch-instance
```

Keep DNS up to date:
```
lfab reroute-dns
```
