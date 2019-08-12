#!/bin/sh

DEPLOY_USER="bmarks"
POLICY_NAME="bmarks-deploy"
POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${POLICY_NAME}"

mkdir -p build
extra/compile-template.py extra/deploy-policy.json.j2 account_id=${AWS_ACCOUNT_ID} > build/deploy-policy.json

aws iam detach-user-policy --user-name ${DEPLOY_USER} --policy-arn ${POLICY_ARN}
aws iam delete-policy --policy-arn ${POLICY_ARN}
aws iam create-policy --policy-name ${POLICY_NAME} --policy-document file://build/deploy-policy.json
aws iam attach-user-policy --user-name ${DEPLOY_USER} --policy-arn ${POLICY_ARN}
