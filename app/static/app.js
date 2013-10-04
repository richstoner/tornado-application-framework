// Based on Angular JS, websockets, Bootstrap, and tornado

'use strict';

// Initialization of angular root application
var tornado_app = angular.module('TornadoApp', []);

// Initialization of angular app controller with necessary scope variables. Inline declaration of external variables
// needed within the controller's scope. State variables (available between controllers using $rootScope). Necessary to
// put these in rootScope to handle pushed data via websocket service.
tornado_app.controller('ApplicationController', ['$scope', '$rootScope', '$timeout', 'WebSocketService', 'uploadService',
    function ($scope, $rootScope, $timeout, WebSocketService, uploadService) {

         // 'files' is an array of JavaScript 'File' objects.
        $scope.files = [];

        $scope.dropbox_status = 'Status';

        $scope.wsinit = WebSocketService.inittest();

        $scope.$watch('files', function (newValue, oldValue) {
            // Only act when our property has changed.
            if (newValue != oldValue) {
                console.log('Controller: $scope.files changed. Start upload.');
                for (var i = 0, length = $scope.files.length; i < length; i++) {
                    // Hand file off to uploadService.
                    uploadService.send($scope.files[i]);
                }
            }
        }, true);

        $rootScope.$on('upload:loadstart', function () {
            console.log('Controller: on `loadstart`');
        });

        $rootScope.$on('upload:error', function () {
            console.log('Controller: on `error`');
        });

        $rootScope.$on('upload:progress', function (e) {
            console.log('Controller: on `progress`');
        });

        $scope.example_action = function () {
            console.log("example action called");
            $rootScope.kickoffresult = WebSocketService.kickoff('http://nvie.com');
        }

            // add an event listener to a Chooser button
        document.getElementById("db-chooser").addEventListener("DbxChooserSuccess",
            function(e) {
                console.log("Here's the chosen file: " + e.files[0].link)
                WebSocketService.selectDropboxFile(e.files);
            }, false);
    }])



tornado_app.directive('fileChange', function () {

    var linker = function ($scope, element, attributes) {
        // onChange, push the files to $scope.files.
        element.bind('change', function (event) {
            var files = event.target.files;
            $scope.$apply(function () {
                for (var i = 0, length = files.length; i < length; i++) {
                    $scope.files.push(files[i]);
                }
            });
        });
    };
    return {
        restrict: 'A',
        link: linker
    };
});

tornado_app.factory('uploadService', ['$rootScope', function ($rootScope) {

    return {
        send: function (file) {
            var data = new FormData(),
                xhr = new XMLHttpRequest();

            // When the request starts.
            xhr.onloadstart = function () {
                console.log('Factory: upload started: ', file.name);
                $rootScope.$emit('upload:loadstart', xhr);
                $rootScope.uploadStatus = 'Uploading';
            };

            // When the request has failed.
            xhr.onerror = function (e) {
                $rootScope.$emit('upload:error', e);
            };

            xhr.onloadprogress = function(e) {

                if (e.lengthComputable)
                {
                    var percentComplete = parseInt((e.loaded / e.total) * 100);
                    console.log("Upload: " + percentComplete + "% complete")
                }
                $rootScope.$emit('upload:progress', e);
            };

            xhr.onloadend = function(e) {
//                console.log(e);
            };

            // Send to server, where we can then access it with $_FILES['file].
            data.append('file', file, file.name);
            xhr.open('POST', '/upload');
            xhr.send(data);
        }
    };
}]);;

// The WebSocketService operates by either linking callbacks to scope variables (promises) or handling spontaneous
// events sent from the tornado application. These events can be status updates or errors not triggered by user input.
tornado_app.factory('WebSocketService', ['$q', '$rootScope', '$http', function ($q, $rootScope) {

    var Service = {};
    var callbacks = {};
    var currentCallbackId = 0;
    var pendingRequests = [];

    var connectStatus = false; // Is the websocket connected?


    // added to handle trickiness in serving via nginx (or other http proxy)
//    var wspath = 'ws://'+location.hostname+(location.port ? ':' +location.port :'') + '/ws';
    var wspath = 'ws://'+location.hostname + ':8001/ws';

    var ws = new WebSocket(wspath);

    ws.onopen = function () {
        console.log("Socket has been opened!");
        connectStatus = true;

    };

    ws.onmessage = function (message) {
        listener(JSON.parse(message.data));
    };

    function sendRequest(request) {
      var defer = $q.defer();
      var callbackId = getCallbackId();
      callbacks[callbackId] = {
        time: new Date(),
        cb:defer
      };
      request.callback_id = callbackId;
      if(!connectStatus) {
        console.log('Saving request until connected');
        pendingRequests.push(request);
      }
      else {
        console.log('Sending request', request);
        ws.send(JSON.stringify(request));
      }
      return defer.promise;
    }

    function listener(data) {

        var messageObj = data;

//      console.log("Received data from websocket: ", messageObj);

        if (callbacks.hasOwnProperty(messageObj.callback_id)) {
            console.log(callbacks[messageObj.callback_id]);
            $rootScope.$apply(callbacks[messageObj.callback_id].cb.resolve(messageObj.data));
            delete callbacks[messageObj.callbackID];
        }
        else {

//            console.log('need to write delegate function that applies push data to rootscope variables (with validation');
//            console.log('unrequested message', messageObj);


            if(messageObj.func == 'update_image'){
                var newdiv = '<div class="col-md-12"><p class="well"><img class="thumbnail" src="'+messageObj.contents.src +'"/><img class="thumbnail" src="'+messageObj.contents.srcproc +'"/></p></div>'
                $("#output-container").append(newdiv);
            }
            else if(messageObj.func == 'update_meta'){
//                console.log(messageObj)
                $rootScope.dropboxStatus = messageObj.contents.state;
                $rootScope.$apply();

            }



//            $rootScope.example_variable = true;
        }
    }

    function getCallbackId() {
        currentCallbackId += 1;
        if (currentCallbackId > 10000) {
            currentCallbackId = 0;
        }
        return currentCallbackId;
    }

    Service.kickoff = function (url) {

        console.log('sending rq kickoff')

        var request = {
            type: 'kickoff_queue',
            url: url
        }

        var promise = sendRequest(request);
        return promise;
    }

    Service.inittest = function () {

        console.log('sending rq inittest')
        var request = {
            type: 'init_test'
        }

        var promise = sendRequest(request);
        return promise;
    }

    Service.selectDropboxFile = function(files){
        console.log('sending files to process request')
        var request = {
            type: 'dropbox',
            files: files
        }
        var promise = sendRequest(request);
        return promise;
    }


    return Service;
}]);



