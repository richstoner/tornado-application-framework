// Based on Angular JS, websockets, Bootstrap, and tornado

// Initialization of angular root application
var tornado_app = angular.module('TornadoApp', []);

// Initialization of angular app controller with necessary scope variables. Inline declaration of external variables
// needed within the controller's scope. State variables (available between controllers using $rootScope). Necessary to
// put these in rootScope to handle pushed data via websocket service.
tornado_app.controller('ApplicationController', ['$scope', '$rootScope', '$timeout', 'WebSocketService', 'uploadService',
    function ($scope, $rootScope, $timeout, WebSocketService, uploadService) {

         // 'files' is an array of JavaScript 'File' objects.
        $scope.files = [];

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

        $scope.example_action = function () {

            console.log("example action called");

            var examplediv = '<div class="col-md-12"><p class="well">Sending job request to count words</p></div>'
            $("#output-container").append(examplediv);

            $rootScope.kickoffresult = WebSocketService.kickoff('http://nvie.com');

        }
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
            };

            // When the request has failed.
            xhr.onerror = function (e) {
                $rootScope.$emit('upload:error', e);
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
tornado_app.factory('WebSocketService', ['$q', '$rootScope', function ($q, $rootScope) {

    var Service = {};
    var callbacks = {};
    var currentCallbackId = 0;
    var ws = new WebSocket("ws://localhost:8888/ws");

    ws.onopen = function () {
        console.log("Socket has been opened!");
    };

    ws.onmessage = function (message) {
        listener(JSON.parse(message.data));
    };

    function sendRequest(request) {
        var defer = $q.defer();
        var callbackId = getCallbackId();
        callbacks[callbackId] = {
            time: new Date(),
            cb: defer
        };
        request.callback_id = callbackId;
        console.log('Sending request', request);
        ws.send(JSON.stringify(request));
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

            console.log('need to write delegate function that applies push data to rootscope variables (with validation');
            console.log('unrequested message', messageObj);

            if(messageObj.func == 'update_image'){

                var newdiv = '<div class="col-md-12"><p class="well"><img class="thumbnail" src="'+messageObj.contents.src +'"/><img class="thumbnail" src="'+messageObj.contents.srcproc +'"/></p></div>'
                $("#output-container").append(newdiv);

            }


            $rootScope.example_variable = true;
            $rootScope.$apply();
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


//    Service.sendWaveformToRemote = function (remote_index, channel, waveform_object) {
//
//        var request = {
//            type: 'send_waveform_to_remote',
//            remote_id: remote_index,
//            remote_channel: channel,
//            waveform: waveform_object
//        }
//
//        var promise = sendRequest(request);
//        return promise;
//    }

    return Service;
}]);



