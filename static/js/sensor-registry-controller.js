angular.module('TempView').controller('SensorRegistryController', ['$scope', '$http', SensorRegistryController]);

function SensorRegistryController($scope, $http) {

  $scope.rooms = [];

  $.mask.definitions['h'] = "[a-f0-9]";
  $("#id_MAC_address").mask("hh:hh:hh:hh:hh:hh");

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
