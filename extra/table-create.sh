#!/bin/sh

aws dynamodb create-table \
	--table-name bmarks_links \
	--key-schema 'AttributeName=id,KeyType=HASH' \
	--attribute-definitions 'AttributeName=id,AttributeType=S' \
	--provisioned-throughput 'ReadCapacityUnits=5,WriteCapacityUnits=5' \
	--tag 'app=bmarks'
