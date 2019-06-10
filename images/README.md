# Biocore On The Amazon Cloud

Biocore uses Jenkins as a project management tool. Jenkins is a very popular 
product among software companies who want to automate their Continuous Integration/Continuous Deployment pipelines.
Jenkins integrates very well across languages, platforms, and operating systems - 
Additionally Jenkins is widely documented and open-source software.

Our Jenkins setting consists on A single master server with multiple worker nodes.
Worker nodes are a hybrid of Amazon EC2 Spot Fleets and MDIBL servers 


## Steps to setup MDIBL's Jenkins master with Spot fleet slaves

### Amazon EC2 Console
1) Create EC2 instance -> Image -> launch configuration -> launch template -> Spot fleet
2) Create cloud user ->  access Key ID and Secret key
```
* Create a new user group "jenkins" (IAM -> Groups)
* Set the following policies for the new group
   a) AmazonS3FullAcess
   b) AmazonEC2FullAccess
* Create a new user "ec2-user" with programtic access(IAM->Users -> Add user)
   a) Add user to "jenkins" group
   b) Create Security credentials (IAM -> ec2-user->security credentials ->Create access Key)
      since the secret key is generated only once, it's advisible to copy
      both the Access Key ID and the security key  and save them in a file somewhere
      in your system where only you can read it
``` 
### Jenkins Server
 Manage Jenkins -> Manage plugins
    a) install Amazon EC2 plugin
    b) install EC2 Fleet plugin
   
#### To add A Spot Fleet
Manage Jenkins ->  Configure System -> Cloud -> Add New Cloud -> Amazon SpotFleet
   ```
    a) AWS Crendentials -> Add -> Jenkins Credentials
       Kind: AWS Creadentials
       Access Key ID : set to access key ID created earlier
       Secret Access Key: ste to security key generated ealier
       
    b) Region : select the region of the fleet created earlier
    c) Spot Fleet: select the availbale fleet 
    d) Launcher: select 'Launch agent agents via SSH'
    e) Credentials: select the cloud user with credentials used 
   ```
#### To Add an Ec2 instance 
Manage Jenkins ->  Configure System -> Cloud -> Add New Cloud -> Amazon EC2
```
     a) AWS Crendentials -> Add -> Jenkins Credentials
       Kind: AWS Creadentials
       Access Key ID : set to access key ID created earlier
       Secret Access Key: ste to security key generated ealier
       
    b) Region : select the region of the fleet created earlier
    c) EC2 Key Pair's Private Key -- copy and paste the keypair used to connect to your EC2 instances
    d) AMI ID -> copy and paste the AMI ID to use for aws console
    e) select the Instance Type
    f) Security group names -> copy and paste the security group name from aws console
    g) Set Remote FS root to /home/ec2-user/jnkins
    h) set Remote user to ec2-user
    
```

## Use Cases
### Jenkins master with on demand slaves
 -- see: https://www.cakesolutions.net/teamblogs/jenkins-and-on-demand-slaves-in-aws
### Jenkins master with dedicated EC2 instances slaves
### Jenkins master with Spot fleet slaves
 ---  https://jenkins.io/blog/2016/06/10/save-costs-with-ec2-spot-fleet/
 --- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-fleet-examples.html

```

# Setting Up Biocore Jenkins on AWS 
STEPS:
1) On EC2 Dashboard Launch and Setup Jenkins Master Node - An EC2 instance
2) SSH to Master node and configure
    * Setup Jenkins Host
    * Install Java 8 on Master Node
    * Create and configure EFS Mount Target to host JENKINS_HOME
    * Create and Configure Swap Space 
    * Create and Configure S3 Mounts
    * Install Jenkins
    * Start Jenkins
    * Set StrictHostKeyChecking to no in /etc/ssh/ssh_config for all users or in ~/.ssh/config for the current user
      This allow the master not to prompt before adding a new host to known_host file
      whenever a new worker is detected
      
3) On AWS console - Setup and Auto Scalling Group for Auto-recovery 
    * Create and configure image for Jenkins host
    * Create and configure Auto scaling 
    * Create and configure auto scaling group
    * Create Load Balancer (classic) -- 
         see: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-getting-started.html
         https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-security-groups.html#elb-vpc-security-groups
    * Set up a load balancer pointing to your your auto Scaling group so that
      you can consistently find your server using the load balancer DNS name (as your server gets
      replaced, its IP address will change.) 
      see: https://docs.aws.amazon.com/autoscaling/ec2/userguide/attach-load-balancer-asg.html
    * Create an AWS CloudFormation template 
 3) Create a Launch Template for jenkins master: 
   https://docs.aws.amazon.com/autoscaling/ec2/userguide/copy-launch-config.html
    




There are various ways You can Launch a Jenkins instance  on AWS cloud But we only explored the following:
1) Traditional deployment, 
2) Containized deployment,
3) Deployment as a web server using Elastic Beanstalk.  

## Setup Jenkins Master Node 

### Deploy Jenkins Instance As a Web Server using Elastic Beanstalk
 Warning:
 EC2 instance launched using Elastic Beanstalk are managed by AWS Elastic Beanstalk - 
 Changes made via SSH WILL BE LOST if the instance is replaced by auto-scaling. 
 For more information on customizing your Elastic Beanstalk environment, see our documentation here: 

### Deploy Jenkins Instance using Traditional Deployment 
#### Launch Configure The Created EC2 instance - master node
#### Install Java 8 on Master Node
#### Create EFS Mount Target to host JENKINS_HOME
#### Add Configure Swap Space to EC2 instances
#### Add Configure S3 Mounts to EC2 Instances 
## Setup and Auto Scalling Group for Auto-recovery 

```

## Appendix 

1) https://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Introduction.html
2) https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html?icmpid=docs_ec2_console
3) https://aws.amazon.com/ec2/instance-types/
4) https://aws.amazon.com/efs/pricing/
5) https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/instance-optimize-cpu.html#instance-specify-cpu-options
6) https://docs.aws.amazon.com/cli/latest/userguide/awscli-install-linux.html
7)https://docs.aws.amazon.com/AWSGettingStartedContinuousDeliveryPipeline/latest/GettingStarted/CICD_Jenkins_Pipeline.html#step-1-build-an-ecs-cluster

8) https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
9) https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html

## Continuous Integration (CI)
## Continuous Deployment (CD)
With continuous deployment, revisions are deployed to a production environment automatically without explicit approval from a developer, making the entire software release process automated. This, in turn, allows for the product to be in front of its customers early on, and for feedback to start coming back to the development teams.

### Updating PATH systemwide to include path to executables installed in non conventional locations
1) ssh to your machine
2) cd to /etc/profile.d/
3) sudo touch biocore.sh
4) sudo edit biocore.sh to add:
```
 # Add /opt/software/bin to the path for sh compatible users
if ! echo $PATH | grep -q /opt/software/bin ; then
  export PATH=/opt/software/bin:$PATH
fi
## Add /opt/software/external/pyenv/bin
if ! echo $PATH | grep -q /opt/software/external/pyenv/bin ; then
  export PATH=/opt/software/external/pyenv/bin:$PATH
fi
## Add /opt/software/external/pyenv/shims
if ! echo $PATH | grep -q /opt/software/external/pyenv/shims ; then
  export PATH=/opt/software/external/pyenv/shims:$PATH
fi
## Add /opt/software/external/pyenv/plugins/pyenv-virtualenv/shims
if ! echo $PATH | grep -q /opt/software/external/pyenv/plugins/pyenv-virtualenv/shims ; then
  export PATH=/opt/software/external/pyenv/plugins/pyenv-virtualenv/shims:$PATH
fi
```
5) Logout then re-login to to test the path


## Adding swap space to EC2 instance:
```

A fix for this problem is to add swap (i.e. paging) space to the instance.

Paging works by creating an area on your hard drive and using it for extra memory, this memory is much slower than normal memory however much more of it is available.

To add this extra space to your instance you type:

## turn the swap off
sudo swapoff -a
sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=10
sudo /sbin/mkswap /var/swap.1
sudo chmod 600 /var/swap.1
## Turn the swap back on 
sudo /sbin/swapon /var/swap.1

This create a swap space of 10MB 

Example:
sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=10
output: 
    sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=10
    10+0 records in
    10+0 records out
    10485760 bytes (10 MB) copied, 0.00656499 s, 1.6 GB/s


To enable it by default after reboot, add this line to /etc/fstab:

/var/swap.1   swap    swap    defaults        0   0
```

## Setting up auto-scaling jenkins
  https://docs.aws.amazon.com/autoscaling/ec2/userguide/attach-load-balancer-asg.html


## Create Amazon EFS Mount Target using two file systems - EFS and S3 file systems
```
#### Create a file system using aws console - https://console.aws.amazon.com/efs/home?region=us-east-1#/filesystems
#### and get the created file system ID
#### launch EC2 instance  using aws console 
#### ssh to the launched EC2 instance and:
* sudo yum update -y
### Install EFS file system
** sudo yum install nfs-utils 
### Install S3 file system  - (https://cloudkul.com/blog/mounting-s3-bucket-linux-ec2-instance/)
** sudo yum update -y
** sudo yum install automake fuse fuse-devel gcc-c++ git libcurl-devel libxml2-devel make openssl-devel
** git clone https://github.com/s3fs-fuse/s3fs-fuse.git
** cd s3fs-fuse
** sudo ./autogen.sh
** sudo ./configure --prefix=/usr --with-openssl
** sudo make
** sudo make install
** which s3fs
** sudo touch /etc/passwd-s3fs
** sudo vim /etc/passwd-s3fs  (then enter awsuser_accesskey:awsuser_secretkey)
** sudo chmod 640 /etc/passwd-s3fs

### Create different mount endpoints on both EFS and S3 file systems
We will create town mount endpoints (/data, /opt/software) one on each file system
** sudo mkdir /data
** sudo mkdir /opt/software
### Create a mount on efs 
** sudo mount -t nfs4 -o vers=4.1 $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone).efs_id.amazonaws.com:/ /data
### Create a mount for your s3 bucket 
** sudo s3fs my-s3-bucket-name -o use_cache=/tmp -o allow_other -o uid=497 -o mp_umask=002 -o multireq_max=20 /data


** sudo vi /etc/fstab  -- and add this line:
s3fs#my-s3-bucket-name   /data   fuse    allow_other,use_cache=/tmp/cache,umask=0002,uid=0,gid=1001       0       0
** sudo vi /etc/fstab (and add this line:
fs-ac75cce4.efs.us-east-1.amazonaws.com:/        /mnt/JENKINS_HOME       nfs    defaults,vers=4.1        0   0

sudo mount -t nfs -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  fs-9cfe74d4.efs.us-east-1.amazonaws.com:/ /data

sudo mount -t nfs -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  fs-56fe741e.efs.us-east-1.amazonaws.com:/ /mnt/transformed

example commands on non-aws servers:
sudo s3fs biocore-data  -o passwd_file=/etc/passwd-s3fs -o uid=500 -o gid=1001 -o mp_umask=002 -o allow_other -o use_cache=/tmp  -o multireq_max=20 /data

sudo s3fs biocore-software  -o passwd_file=/etc/passwd-s3fs -o uid=500 -o gid=1001 -o mp_umask=002 -o allow_other -o use_cache=/tmp  -o multireq_max=20 /opt/software

##### The fstab file
fs-9cfe74d4.efs.us-east-1.amazonaws.com:/       /data    nfs     nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport       0       0
fs-3cda4f74.efs.us-east-1.amazonaws.com:/       /opt/software   nfs     nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport       0       0               
```
## Install Jenkins

sudo wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins-ci.org/redhat/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat/jenkins.io.key 
sudo yum install jenkins -y 
sudo chown jenkins:jenkins /mnt/JENKINS_HOME
sudo vi /etc/sysconfig/jenkins  ( and change JENKINS_HOME path to /mnt/JENKINS_HOME)

Before starting Jenkins Make sure jaba 8 is installed if not run:
sudo yum install java-1.8.0
sudo yum remove java-1.7.0-openjdk
sudo service jenkins start
And follow instructions

```
