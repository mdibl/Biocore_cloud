# Setting Up Biocore Virtual Private Cloud network (VPCN)
## Why The Cloud?
## Jenkins
Jenkins is a very popular product among software companies who want to automate their Continuous Integration/Continuous Deployment pipelines.
Jenkins integrates very well across languages, platforms, and operating systems - Additionally Jenkins is widely documented
 and open-source software.

Our Jenkins setting consist on A single, large master server with multiple worker nodes connected to it.

There are various ways You can Launch a Jenkins instance  on AWS cloud But we only explored the following:
1) Traditional deployment, 
2) Containized deployment,
3) Deployment as a web server using Elastic Beanstalk.  

### Deploy Jenkins Instance As a Web Server using Elastic Beanstalk
```
 Warning:
 EC2 instance launched using Elastic Beanstalk are managed by AWS Elastic Beanstalk - 
 Changes made via SSH WILL BE LOST if the instance is replaced by auto-scaling. 
 For more information on customizing your Elastic Beanstalk environment, see our documentation here: 
 http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/customize-containers-ec2.html
```
### Deploy Jenkins Instance using Traditional Deployment 
#### Launch Configure The Created EC2 instance - master node
#### Install Java 8 on Master Node
#### Create EFS Mount Target to host JENKINS_HOME
#### Configure and Launch Jenkins Master Node
#### Add and Configure Swap Space to EC2 instances
#### Add and Configure S3 Mounts to EC2 Instances 
#### Setup and Auto Scalling Group for Auto-recovery 

## Galaxy
## Cost Estimate

## Appendix 

1) https://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Introduction.html
2) https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html?icmpid=docs_ec2_console
## Continuous Integration (CI)
## Continuous Deployment (CD)
With continuous deployment, revisions are deployed to a production environment automatically without explicit approval from a developer, making the entire software release process automated. This, in turn, allows for the product to be in front of its customers early on, and for feedback to start coming back to the development teams.

```
Adding swap space to EC2 instance:

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


## Setting up auto-scaling jenkins
### Create Amazon EFS Mount Target
Use console 
### launch EC2 instance - jenkins master node
sudo yum update -y
sudo yum install nfs-utils 
sudo mkdir /mnt/JENKINS_HOME
sudo mount -t nfs4 -o vers=4.1 $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone).fs-ac75cce4.efs.us-east-1.amazonaws.com:/ /mnt/JENKINS_HOME

sudo wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins-ci.org/redhat/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat/jenkins.io.key 
sudo yum install jenkins -y 
sudo chown jenkins:jenkins /mnt/JENKINS_HOME
sudo vi /etc/sysconfig/jenkins  ( and change JENKINS_HOME path to /mnt/JENKINS_HOME)
sudo vi /etc/fstab (and add this line:
fs-ac75cce4.efs.us-east-1.amazonaws.com:/        /mnt/JENKINS_HOME       nfs    defaults,vers=4.1        0   0
)
Before starting Jenkins Make sure jaba 8 is installed if not run:
sudo yum install java-1.8.0
sudo yum remove java-1.7.0-openjdk
sudo service jenkins start
And follow instructions

When your instance is up and running do:
1) Install s3 File system and Create mounts to our s3 buckets (https://cloudkul.com/blog/mounting-s3-bucket-linux-ec2-instance/)
a) Install s3fs
sudo yum update -y
sudo yum install automake fuse fuse-devel gcc-c++ git libcurl-devel libxml2-devel make openssl-devel
git clone https://github.com/s3fs-fuse/s3fs-fuse.git
cd s3fs-fuse
sudo ./autogen.sh
sudo ./configure --prefix=/usr --with-openssl
sudo make
sudo make install
which s3fs
sudo touch /etc/passwd-s3fs
sudo vim /etc/passwd-s3fs  (then enter jenkins_accesskey:jenkins_secretkey)
sudo chmod 640 /etc/passwd-s3fs
sudo mkdir /mnt/data
sudo mkdir /mnt/software
sudo mkdir /mnt/logs
sudo chown jenkins:jenkins /mnt/data
sudo chown jenkins:jenkins /mnt/software
sudo chown jenkins:jenkins /mnt/logs
sudo s3fs biocore-data -o use_cache=/tmp -o allow_other -o uid=497 -o mp_umask=002 -o multireq_max=20 /mnt/data
sudo s3fs biocore-software -o use_cache=/tmp -o allow_other -o uid=497 -o mp_umask=002 -o multireq_max=20 /mnt/software
sudo s3fs biocore-logs -o use_cache=/tmp -o allow_other -o uid=497 -o mp_umask=002 -o multireq_max=20 /mnt/logs

sudo vi  /etc/rc.local 
and add the following lines:
  sudo s3fs biocore-data -o use_cache=/tmp -o allow_other -o uid=497 -o mp_umask=002 -o multireq_max=20 /mnt/data
  sudo s3fs biocore-software -o use_cache=/tmp -o allow_other -o uid=497 -o mp_umask=002 -o multireq_max=20 /mnt/software
  sudo s3fs biocore-logs -o use_cache=/tmp -o allow_other -o uid=497 -o mp_umask=002 -o multireq_max=20 /mnt/logs

Add swap space to the instance - see steps earlier


```
