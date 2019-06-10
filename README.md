# Biocore On The Amazon Cloud

Biocore uses Jenkins as a project management tool. Jenkins is a very popular 
product among software companies who want to automate their Continuous Integration/Continuous Deployment pipelines.
Jenkins integrates very well across languages, platforms, and operating systems - 
Additionally Jenkins is widely documented and open-source software.

Our Jenkins setting consists on A single master server with multiple worker nodes.
Worker nodes are a hybrid of Amazon EC2 instances and MDIBL servers 

See:
     [<img src="images/biocore-aws-hybrid-system.png">](biocore-aws-hybrid-system.png)


## Package Overview
  
This is a base directory  for **scripts and configuration files** used to
run a given pipeline.

See::



 [<img src="images/biocore-pipelines-scripts.png">](biocore-pipelines-scripts.png)


You have the following four options to run your pipeline :

```
 Option 1: Run multiple pipelines on local servers
         gen-project-config => json_generator => gen-pipeline-pcf => pipelines-in-parallel/local => gen-matrix

 Option 2: Run multiple pipelines on AWS cloud servers
         gen-project-config => json_generator => gen-pipeline-pcf => pipelines-in-parallel/cloud => gen-matrix

 Option 3: Run single pipeline on local server
         gen-project-config => json_generator => gen-pipeline-pcf => single-sample-pipeline-local

  Option 4: Run single pipeline on AWS Instance
         gen-project-config => json_generator => gen-pipeline-pcf => single-sample-pipeline-local => gen-matrix

## Scripts and Files Organization

**Documentation ( docs/)**

All the associated documents - pdf, words, powerpoint,.. - are stored under docs/

**Images (images/)**

All associated images are under the images sub-directory


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

