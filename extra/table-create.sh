#!/bin/sh

aws dynamodb create-table \
	--table-name links1 \
	--key-schema 'AttributeName=id,KeyType=HASH' \
	--attribute-definitions 'AttributeName=id,AttributeType=S' \
	--provisioned-throughput 'ReadCapacityUnits=5,WriteCapacityUnits=5'
