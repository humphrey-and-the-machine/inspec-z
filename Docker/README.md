Table of content
- [How to run this image on Mac OS X - Quick start](#-how-to-run-this-image-on-mac-os-x---quick-start)
- [How to run this image on Mac OS X - Long version](#-how-to-run-this-image-on-mac-os-x---long-version)
- [How to load your data to the image](#-how-to-load-your-data-to-the-image)

# How to run this image on Mac OS X - Quick start

TODO: Provide more secure way to run the X11

## Prerequisites

### Install XQuartz

Official website: https://www.xquartz.org/
 
- Download the .dmg, execute it and follow the instructions

### Configure XQuartz

1. Execute XQuartz. In a terminal type:
  ```bash
  open -a xquartz
  ```
2. Open the `Preferences...` menu
3. Go to the Security tab and check the box `Allow connections from network clients`

## Run the container

```bash
open -a xquartz
/opt/X11/bin/xhost +
docker run \
    --rm \
    -v $(pwd)/config_files/dockerConfig.yaml:/mnt/config.yaml \
    -v $(pwd)/data:/app/data \
    -e DISPLAY=$(ifconfig en0 | grep "inet " | awk '{print $2}'):0 \
    douchy/inspec-z:1.0.0
```

# How to run this image on Mac OS X - Long version
## How to build the image

From the root of the git repository:
```bash
docker build -t inspec-z:1.0.0 -f Docker/Dockerfile .
```

Expected output using buildx (default engine since 3.2.0 https://docs.docker.com/docker-for-mac/release-notes/#docker-desktop-320):
```bash
 => => naming to docker.io/library/inspec-z:1.0.0                    0.0s
```

## How to run this image 

TODO: Provide more secure way to run the X11

### Prerequisites

#### Install XQuartz

Official website: https://www.xquartz.org/
 
- Download the .dmg, execute it and follow the instructions

#### Configure XQuartz

1. Execute XQuartz. In a terminal type:
  ```bash
  open -a xquartz
  ```
2. Open the `Preferences...` menu
3. Go to the Security tab and check the box `Allow connections from network clients`

#### Disable access control for XQuartz

In a terminal type:
  ```bash
  /opt/X11/bin/xhost +
  ```
  Expected result:
  ```bash
  access control disabled, clients can connect from any host
  ```

#### Identify your IP 

In a terminal type:
  ```bash
  ifconfig en0 | grep "inet " | awk '{print $2}'
  ```
  Expected result an ipv4 address for example
  ```bash
  192.168.1.102
  ```

### Run the container

Execute this command from the root of the git repository.
Replace `<YOUR_IP>` by the value retrieved from the [Identify your IP](###-identify-your-ip) section
```Bash
docker run \
    --rm \
    -v $(pwd)/config_files/dockerConfig.yaml:/mnt/config.yaml \
    -v $(pwd)/data:/app/data \
    -e DISPLAY=<YOUR_IP>:0 \
    inspec-z:1.0.0
```

### Startup script assuming XQuartz installation and configuration is already done

```bash
open -a xquartz
/opt/X11/bin/xhost +
docker run \
    --rm \
    -v $(pwd)/config_files/dockerConfig.yaml:/mnt/config.yaml \
    -v $(pwd)/data:/app/data \
    -e DISPLAY=$(ifconfig en0 | grep "inet " | awk '{print $2}'):0 \
    inspec-z:1.0.0
```

# How to load your data to the image

Data loaded in the container is controlled via the second `-v` option visible in [Run the container](##-run-the-container).

To use your own data, update the value of the left hand side of `':'`.

In the example [Run the container
](##-run-the-container) the value to change is `$(pwd)/data`. 

`/!\` The right hand side of the `-v` variable `/app/data` instruct the container where to find the data and should not be changed. `/!\`

Official documentation related to the `-v` option can be found at see https://docs.docker.com/engine/reference/run/#volume-shared-filesystems.
