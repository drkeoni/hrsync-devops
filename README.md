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
lfab start-instance
```

Keep DNS up to date:
```
lfab reroute-dns
```

Pull latest docker image onto server:
```
rfab docker-pull
```

Stop the EC2 instance:
```
lfab stop-instance
```

(n.b. use `lfab` for local commands and `rfab` for remote commands)
