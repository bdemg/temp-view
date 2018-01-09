angular.module('TempView').controller('GeneralReportsController', ['$scope', '$http', ReportsController]);

function ReportsController($scope, $http) {

  $scope.tempReadouts = [];

  $scope.getTemperatureReadouts = function(){

    $http.get("/general_reports/mac=" + $scope.sensor + "/startDate=" + document.getElementById("id_start_date").value + "/range=" + $scope.range).then(function (response){

      $scope.tempReadouts = response.data;

      var chartTitle;

      switch ($scope.range) {
        case "day":
          chartTitle = "Promedio de temperaturas por hora del día";
          break;

        case "week":
          chartTitle = "Promedio de temperaturas por dia de la semana";
          break;

        case "month":
          chartTitle = "Promedio de temperaturas por dia del mes";
          break;

        case "year":
          chartTitle = "Promedio de temperaturas por mes del año";
          break;
        default:
         chartTitle = "Gráfica de temperaturas";
      }

      // Create the data table.
      var data = new google.visualization.DataTable();
      data.addColumn('string', 'Tiempo');
      data.addColumn('number', 'Temperatura');
      data.addRows($scope.tempReadouts.individual_averages);

      // Set chart options
      var options = {'title': chartTitle,
                     'width':1200,
                     'height':400,
                     hAxis: {
                       direction: 1,
                       slantedText: true,
                       slantedTextAngle: 45 // here you can even use 180
                    }
    };

      // Instantiate and draw our chart, passing in some options.
      var chart = new google.visualization.LineChart(document.getElementById("chart_div"));
      chart.draw(data, options);

      $('#chart_div').show();
    });
  }
}
