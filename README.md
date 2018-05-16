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
```
