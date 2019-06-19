**Lambda functions for PODAAC Disaster Recovery**

- [Environment](#environment)
- [Setting up your development environment](#setting-up-your-development-environment)
  * [Git clone](#git-clone)
  * [Prepare the virtual environment](#prepare-the-virtual-environment)
    + [Windows](#windows)
  * [Pycharm](#pycharm)
- [Helpful Links](#helpful-links)


# Environment
```
   Python3.6
   Cmder
```

# Setting up your development environment

## Git clone
>git clone https://git.earthdata.nasa.gov/scm/pocumulus/dr-podaac-swot.git

Create an alias called origin to your main remote repository (in this case, ECC):
>git remote add origin https://erosuser@git.earthdata.nasa.gov/scm/pocumulus/dr-podaac-swot.git

## Prepare the virtual environment.

### Windows:
```
1.  Substitute the directory where you cloned git repo or installed this README.md for $SCRIPTDIR. ex: c:\devpy\poswotdr

        cd $SCRIPTDIR

2.  Run
        conda create -n podr python=3.6

	to create a virtual environment in the Anaconda envs directory

3.  Run

		activate podr

	to activate the virtual environment.

4.  Execute

		pip install --upgrade pip

	to get the latest python package installer.

5.  Execute

        export PIP_DEFAULT_TIMEOUT=100
		pip install boto3

		for development:
		pip install coverage
		pip install nose
		pip install pylint

	to get all the python requirements.

6.   Install the Amazon CLI
        pip3 install awscli --upgrade --user

        aws configure
          AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
          AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
          Default region name [None]: us-west-2
          Default output format [None]: json

```

## Pycharm
If you choose to use Pycharm for development:
Substitute the directory where you cloned git repo or installed this README.md for $SCRIPTDIR. ex: c:\devpy\poswotdr
Open $SCRIPTDIR
Ctrl-1 :  project view
Expand poswotdr

File | Settings
Project Interpreter
   windows:
       File|Settings|Project Tasks|Project Interpreter
       Set value to: Python3.6 (lambda) C:\Anaconda3\env\podr\python.exe

# Helpful Links
```
https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html
```
