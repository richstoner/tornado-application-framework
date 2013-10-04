tornado-application-framework
=============================

A standalone tornado backend that interacts with a angular+bootstrap frontend via websockets

## Design

* Tornado handles communication between frontend via http & websockets
* Angular handles frontend model and user interface
* RQ (redis queue) handles long running jobs on local or distributed resources

## How to use this platform

### Asynchronous binding of data from tornado to angular scope variables

In plain language, this mechanism allows you to set a variable within an angular scope to the results of a function
run on the backend.

    $scope.variable_needed = WebSocketService.getVariableNeeded();

**getVariableNeeded** is a function defined in the websocket service and crafts a message with function to be called,
a callback identifier, and any additional arguments to pass withit. You can write your own function such as
getVariableNeeded or create a more generalized version to limit code length. 

From there, the tornado receives the ws message, parses the function to be called, executes that function, and then returns the result via ws message. The frontend recieves this message, resolves where it initiated from, and updates the appropriate variables ($scope.variable_needed in this case). This triggers a scope update in angular, which propagates to any UI dependencies.

### Distributed queue-based processing

In plain language, this mechanism allows you to kick off a long job via RQ (redis queue). Jobs are defined in standalone modules outside of the main tornado code. The tornado code iterates through a shared array of currently queued or running tasks at a fixed interval (~5 seconds). If it detects a finished job, it pulls the results and sends it to the connected client (TODO: it should store the result in a database somewhere as well). 



## Platform

Currently, this application depends on:

1. tornado
2. rq (redis queue)
3. redis
4. angular.js
5. jquery
6. bootstrap 3

### Current dev setup

tornado and rq installed via pip
redis-server installed via homebrew
frontend dependencies (angular, jquery, bootstrap) installed via bower
interactive deploy on vagrant, running 12.04, managed by fabric

### Example jobs

We're using scipy, sci-kit image, and requests to demonstrate long running jobs via rq.


## Getting Started with a running instance

1) In the root directory, launch a vagrant instance (you'll need to download a precise64 box via the vagrant install instructions).

	vagrant up;
	
2) Verify the vm is working

	fab vagrant sysinfo

Output:
	
	[localhost] local: vagrant ssh-config | grep IdentityFile
	[127.0.0.1:2222] Executing task 'sysinfo'
	[127.0.0.1:2222] run: uname -a
	[127.0.0.1:2222] out: Linux precise64 3.2.0-23-generic #36-Ubuntu SMP Tue Apr 10 20:39:51 UTC 2012 x86_64 x86_64 x86_64 GNU/Linux
	[127.0.0.1:2222] out: 
	
	[127.0.0.1:2222] run: lsb_release -a
	[127.0.0.1:2222] out: No LSB modules are available.
	[127.0.0.1:2222] out: Distributor ID:	Ubuntu
	[127.0.0.1:2222] out: Description:	Ubuntu 12.04.3 LTS
	[127.0.0.1:2222] out: Release:	12.04
	[127.0.0.1:2222] out: Codename:	precise

3) Provision the VM using fab (this currently does more than it needs to - lots of vestigial code)

	fab vagrant base
	fab vagrant externals
	
4) Start the nginx server

	fab vagrant startnginx
	
5) 
	
	
	













