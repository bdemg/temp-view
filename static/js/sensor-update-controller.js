angular.module('TempView').controller('SensorUpdateController', ['$scope', '$http', SensorUpdateController]);

function SensorUpdateController($scope, $http) {

  $scope.rooms = [];

  $.mask.definitions['h'] = "[a-f0-9]";
  $("#id_MAC_address").mask("hh:hh:hh:hh:hh:hh");

  var selected_building = $("#id_building").val();
  $http.get("/rooms/building=" + selected_building).then(function (response){
    $scope.rooms = response.data;
    setTimeout(function () {$("#id_room").val($("#id_selected_room").val());}, 10);
  });


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
