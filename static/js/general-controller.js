angular.module('TempView').controller('GeneralController', ['$scope', '$http', GeneralController]);

function GeneralController($scope, $http) {

  var SENSOR_REFRESH_TIMEOUT = 6000;
  refreshSensors();

  $scope.tempAverage = function (sensors){
    var average = 0;
    var validSensors = 0;

    for(var i = 0; i < sensors.length; i++){

      if(!isNaN(parseFloat(sensors[i].fields.last_known_temperature))){

        var temp = parseFloat(sensors[i].fields.last_known_temperature)
        average = average + temp;
        validSensors++;
      }
    }
    if(average === 0){
      return "N/A";
    } else{
      return average/validSensors;
    }
  }


  function refreshSensors(){
    $http.get("/temperature_sensors/").then(function (response){

      $scope.temperatureSensors = response.data;

      $scope.temperatureSensors.sort(function(a, b){
        return a.fields.building.localeCompare(b.fields.building);
      });
      
      setTimeout(refreshSensors, SENSOR_REFRESH_TIMEOUT);
    }, function(response){

      setTimeout(refreshSensors, SENSOR_REFRESH_TIMEOUT);
    });
  }
}
