FROM amazonlinux:2

# This image can be used to run unit tests for ORCA.
# TODO: remove packages from tasks/lambda/requirements-dev.txt and tasks/lambda/requirements.txt 
# except coverage, pytest, fastjsonschema and shared libraries- throws no module found error

ENV TERRAFORM_VERSION "0.13.6"

# CLI utilities
RUN yum install -y gcc git make openssl wget zip unzip tar

# install Python 3 and pip
RUN \
yum install -y python3-devel && \
yum -y install python3-pip && \
pip3 install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org

# AWS & Terraform
RUN \
yum install -y awscli && \
wget "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" && \
unzip *.zip && \
chmod +x terraform && \
mv terraform /usr/local/bin

# Install and configure git-secrets
RUN \
cd /root && \
git clone https://github.com/awslabs/git-secrets.git && \
cd git-secrets && \
make install && \
git secrets --register-aws --global && \
git secrets --install ~/.git-templates/git-secrets && \
git config --global init.templateDir ~/.git-templates/git-secrets

# SSM SessionManager plugin
RUN \
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/linux_64bit/session-manager-plugin.rpm" -o "session-manager-plugin.rpm" && \
yum install -y session-manager-plugin.rpm

# Install all necessary packages
RUN \
pip3 install psycopg2-binary==2.8.6 SQLAlchemy==1.4.11 pydoc-markdown==4.5.0 boto3==1.18.40 fastjsonschema==2.15.1 cumulus-message-adapter-python==2.0.1 moto[sqs,s3]==2.2.8 bandit==1.7.0 safety==1.10.3 flake8==4.0.1 black==21.12b0 isort==5.10.1

WORKDIR /data
CMD ["/bin/bash"]
 



