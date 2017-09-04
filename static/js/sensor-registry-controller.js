angular.module('TempView').controller('SensorRegistryController', ['$scope', '$http', SensorRegistryController]);

function SensorRegistryController($scope, $http) {

  $scope.rooms = [];

  $("#id_building").change(function(){
    $("#id_room").val("");
    getRoomsForSelectedBuilding($("#id_building").val());
  });

  function getRoomsForSelectedBuilding(building){

    $http.get("/rooms/building=" + building).then(function (response){

      $scope.rooms = response.data;
    });
  }
}
