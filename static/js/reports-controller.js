angular.module('TempView').controller('ReportsController', ['$scope', '$http', ReportsController]);

function ReportsController($scope, $http) {

  $scope.tempReadouts = [];

  $scope.getTemperatureReadouts = function(){

    $http.get("/readouts/mac=" + $scope.sensor + "/startDate=" + $scope.startDate + "/endDate=" + $scope.endDate).then(function (response){

      $scope.tempReadouts = response.data;
    });
  }
}
