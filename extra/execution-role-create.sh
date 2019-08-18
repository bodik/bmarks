#!/bin/sh

ROLE_NAME="bmarks-execution-role"
POLICY_NAME="bmarks-execution-role-policy"
POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${POLICY_NAME}"

mkdir -p build
extra/compile_template.py extra/execution-role-policy.json.j2 aws_account_id=${AWS_ACCOUNT_ID} > build/execution-role-policy.json

aws iam detach-role-policy --role-name ${ROLE_NAME} --policy-arn ${POLICY_ARN}
aws iam delete-policy --policy-arn ${POLICY_ARN}
aws iam delete-role --role-name ${ROLE_NAME}

aws iam create-role --role-name ${ROLE_NAME} --assume-role-policy-document file://extra/execution-role-policy-document.json
aws iam create-policy --policy-name ${POLICY_NAME} --policy-document file://build/execution-role-policy.json
aws iam attach-role-policy --role-name ${ROLE_NAME} --policy-arn ${POLICY_ARN}
