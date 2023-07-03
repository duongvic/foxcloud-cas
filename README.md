# foxcloud
##I. Prerequisite
If you want to use ceph api. To make sure that **python3-librados** and **python3-librbd** were installed. <br/>
Please follow this step to install manually
### Step1: Check ceph version
```shell script
ceph --version 
```
Result:
```text
ceph --version
ceph version 14.2.11 (f7fdb2f52131f54b891a2ec99d8205561242cdaf) nautilus (stable)
```
### Step2: Find correctly target packages  <br/>
### 1. Centos
Refer [Ceph Repo](https://download.ceph.com/rpm-nautilus/el7/x86_64/)
```shell script
# Install librados2
yum install https://download.ceph.com/rpm-nautilus/el7/x86_64/librados2-14.2.11-0.el7.x86_64.rpm -y
yum install https://download.ceph.com/rpm-nautilus/el7/x86_64/librados-devel-14.2.11-0.el7.x86_64.rpm -y
yum install https://download.ceph.com/rpm-nautilus/el7/x86_64/python3-rados-14.2.11-0.el7.x86_64.rpm -y

# Install librbd
yum install https://download.ceph.com/rpm-nautilus/el7/x86_64/python3-rbd-14.2.11-0.el7.x86_64.rpm -y
yum install https://download.ceph.com/rpm-nautilus/el7/x86_64/librbd1-14.2.11-0.el7.x86_64.rpm -y
yum install https://download.ceph.com/rpm-nautilus/el7/x86_64/librbd-devel-14.2.11-0.el7.x86_64.rpm -y
```
Result:
```shell script
pip3 list | grep rados
# rados (2.0.0)
pip3 list | grep rbd
# rbd (2.0.0)
```
#### 2. Ubuntu <br/>
Refer [Repo](https://pkgs.org/search/?q=librbd)

## II. How to install library
```shell script
sudo pip3 install git+https://github.com/khanhct/foxcloud.git@ussuri#egg=foxcloud
```
### Install python-ldap
```shell script
sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev -y
# or
sudo yum install python-devel openldap-devel
```

## III. Other
**Install python 3.7.2. It is compatible with ceph version 14.2.11**
```shell script
sudo yum install gcc openssl-devel bzip2-devel
sudo wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz
sudo tar xzf Python-3.7.2.tgz
cd Python-3.7.2.tgz
./configure --enable-optimizations
make altinstall
```