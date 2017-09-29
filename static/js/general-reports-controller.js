angular.module('TempView').controller('GeneralReportsController', ['$scope', '$http', ReportsController]);

function ReportsController($scope, $http) {

  $scope.tempReadouts = [];

  $scope.getTemperatureReadouts = function(){

    $http.get("/general_reports/mac=" + $scope.sensor + "/startDate=" + document.getElementById("id_start_date").value + "/range=" + $scope.range).then(function (response){

      $scope.tempReadouts = response.data;
    });
  }
}
