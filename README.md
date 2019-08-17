# bmarks -- bodik bookmarks

First aws webapp


## Install and deploy

```
cp .env.example .env

# configure admin credentials, push policies and create table
editor .env
. .env
sh extra/deploy-policy-create.sh
sh extra/execution-role-create.sh
sh extra/table-create.sh

# configure deployment credentials, application parameters and push application
editor .env
. .env
make zappa_settings
zappa deploy dev
zappa update dev
zappa update -n dev
```

## Development

```
cp .env.example .env

# configure local dynamo instance and application parameters
editor .env
. .env

make dynamo
make lint
make test
make coverage
make devserver
```


## IAM

AWS ecosystem is managed through web console or cli. The main account is called
root user and it's not advised to generate access keys for or pass users
credentials to the management tools. For normal operations IAM
users, roles and policies should be created to define fine-grained access policy.

For this project it's required to setup:
  * deploy user and attach deploy-policy for lambda, s3, apigateway and cloudlogs management
  * execution role and policy, which is to be passed to the aws components at the time of execution of the application

Basic policies should be refined from default zappa policies created by running
zappa with example deploy policy from [1]. They should be further restricted in
the terms of allowed actions on services and constrained to the specific
resources to achieve least-privilege principle on all components.


## References

[1] https://github.com/Miserlou/Zappa/blob/master/example/policy/deploy.json.
