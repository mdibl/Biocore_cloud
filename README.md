# Setting Up Biocore Virtual Private Cloud network (VPCN)
## Why The Cloud?
## Jenkins
### Create A Web Server 
### Configure The Created EC2 instance
### Configure Jenkins Master Node
### Add and Configure Worker Node
##  Add Swap Space to EC2 instances
##  Add S3 Mounts to EC2 Instances 
##  Create Worker Node image and add more nodes
## Galaxy
## Cost Estimate

## Appendix 

1) https://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Introduction.html
2) https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html?icmpid=docs_ec2_console

```
Adding swap space to EC2 instance:

A fix for this problem is to add swap (i.e. paging) space to the instance.

Paging works by creating an area on your hard drive and using it for extra memory, this memory is much slower than normal memory however much more of it is available.

To add this extra space to your instance you type:

sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024
sudo /sbin/mkswap /var/swap.1
sudo chmod 600 /var/swap.1
sudo /sbin/swapon /var/swap.1
If you need more than 1024 then change that to something higher.

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
Before starting Jenkins Make sure jaba 8 is installed if not run:
sudo yum install java-1.8.0
sudo yum remove java-1.7.0-openjdk
sudo service jenkins start
And follow instructions
```
