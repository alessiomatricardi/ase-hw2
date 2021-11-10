# My message in a bottle - ASE course project made by squad 4

[![Build Status](https://app.travis-ci.com/alessiomatricardi/ase-hw2.svg?token=27PrqUDodvhxobq6Hmxx&branch=master)](https://app.travis-ci.com/alessiomatricardi/ase-hw2) [![Coverage Status](https://coveralls.io/repos/github/alessiomatricardi/ase-hw2/badge.svg?branch=master)](https://coveralls.io/github/alessiomatricardi/ase-hw2?branch=master)

## IMPORTANT Requirements
Be sure to have `python3` and `pip3` installed in your machine

## Setup steps

### 0. Clone the repository
Download the repository from [Github archives](https://github.com/alessiomatricardi/ase-hw2/archive/refs/heads/master.zip) and extract it. After that, enter inside the root of the project typing

```
cd ase-hw2
```

Or clone it with the following command (`git` is required to be installed in your machine)

```
git clone https://github.com/alessiomatricardi/ase-hw2.git && cd ase-hw2
```


### 1. (SUGGESTED) Setup a virtual enviroment
To setup a virtual enviroment type the following commands

```
python3 -m venv venv && source venv/bin/activate
```

### 2. Install requirements
Install application requirements inside the virtual enviroment by writing the following commands

```
bash install.sh
```

Or

```
pip3 install -r requirements.txt && python3 -m spacy download en
```

### 3. Run
Run the application by typing

```
bash run.sh
```

### Tests
To run tests execute the following command

```
bash test.sh
```

Alternatively, you can execute a test using `pytest`, but you have to remove all that data which are created during the application running or tests
Try this!

```
rm mmiab.db
rm -rf monolith/static/attachments
pytest --cov monolith
```

# All-in-one solution
Execute
```
bash start.sh
```
to perform both requirement installation and run the app
