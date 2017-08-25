angular.module('TempView').controller('GeneralController', ['$scope', '$http', GeneralController]);

function GeneralController($scope, $http) {

  var SENSOR_REFRESH_TIMEOUT = 6000;
  refreshSensors();

  function refreshSensors(){
    $http.get("/temperature_sensors/").then(function (response){

      $scope.temperatureSensors = response.data;
      setTimeout(refreshSensors, SENSOR_REFRESH_TIMEOUT);
    }, function(response){

      setTimeout(refreshSensors, SENSOR_REFRESH_TIMEOUT);
    });
  }
}
