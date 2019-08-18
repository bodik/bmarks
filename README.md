# bmarks -- simple bookmark webapp running on aws

Staying up-to-date in any field of study is hard and continuous process, in
computer security is just a little bit harder. This app servers a few purposes:
practice python coding, learn to work  with AWS ecosystem and to provide
sortable and taggable haystack of interesting links for reading.


## On IAM policies

AWS ecosystem is guarded by policies and roles. Root account should be used as
less as possible. For regular development a deploy policy (set of permissions
for developer) was refined from [1], execution policy (set of permissions
delegated to aws components executing the application code) was refined from
default zappa created execution policy.


## AWS Setup

```
# configure admin credentials
cp .env.example .env
editor .env
. .env

# make venv
make venv
. venv/bin/activate
pip install -r requirements-aws.txt 

# push policies and create table
sh extra/deploy-policy-create.sh
sh extra/execution-role-create.sh
sh extra/table-create.sh
```

## Deployment

```
# configure deployment credentials and application parameters
cp .env.example .env
editor .env
. .env

# make venv
make venv
. venv/bin/activate
make install-deps

# deploy the application
make zappa_settings
zappa deploy dev
zappa update dev
zappa update -n dev
```

## Development

```
# configure local dynamo instance and application parameters
cp .env.example .env
editor .env
. .env

# make venv
make venv
. venv/bin/activate
make install-deps

# run development server
make dynamo
make lint
make test
make coverage
make devserver
```

## References

[1] https://github.com/Miserlou/Zappa/blob/master/example/policy/deploy.json
