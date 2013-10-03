tornado-application-framework
=============================

A standalone tornado backend that interacts with a angular+bootstrap frontend via websockets

## Design

Tornado handles communication between frontend via http & websockets
Angular handles frontend model and user interface
RQ (redis queue) handles long running jobs on local or distributed resources

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

In plain language, this mechanism allows you to kick off a long job via RQ (redis queue). 






