# Biocore On The Amazon Cloud

Biocore uses Jenkins as a project management tool. Jenkins is a very popular 
product among software companies who want to automate their Continuous Integration/Continuous Deployment pipelines.
Jenkins integrates very well across languages, platforms, and operating systems - 
Additionally Jenkins is widely documented and open-source software.

Our Jenkins setting consists on A single master server with multiple worker nodes.
Worker nodes are a hybrid of Amazon EC2 instances and MDIBL servers 

See:
     [<img src="images/biocore-aws-hybrid-system.png">](biocore-aws-hybrid-system.png)

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

