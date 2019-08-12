# bmarks -- bodik bookmarks

First aws webapp

## TODO

* how to properly setup IAM with/for zappa as least-privilege
	* has to add administrator access for bootstrap
	* has to add GetFunction, CreateFunction for Lambda manualy

	jneves 11:13 PM
	For the execution role, I'd start with the generated one and reduce permissions and replace the asterisks by as much specific principals as possible. For deploy permissions start with https://github.com/Miserlou/Zappa/blob/master/example/policy/deploy.json and do the same.
