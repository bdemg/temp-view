angular.module('TempView').controller('GeneralReportsController', ['$scope', '$http', ReportsController]);

function ReportsController($scope, $http) {

  // Load the Visualization API and the corechart package.
  google.charts.load('current', {'packages':['corechart'], 'language': 'es'});

  // Set a callback to run when the Google Visualization API is loaded.
  google.charts.setOnLoadCallback(hideChart);

  // Callback that creates and populates a data table,
  // instantiates the pie chart, passes in the data and
  // draws it.
  function hideChart() {

    $('#chart_div').hide();
  }

  $("#id_start_date").on("change", function() {
    this.setAttribute(
        "data-date",
        moment(this.value, "YYYY-MM-DD")
        .format( this.getAttribute("data-date-format") )
    )
  }).trigger("change");

  $scope.tempReadouts = [];

  function parseFloatReadouts(){

    for (var readout = 0; readout < $scope.tempReadouts.individual_averages.length; readout++) {

      $scope.tempReadouts.individual_averages[readout][1] = parseFloat($scope.tempReadouts.individual_averages[readout][1]);
    }

    $scope.tempReadouts.general_average = parseFloat($scope.tempReadouts.general_average);
  }

  $scope.getTemperatureReadouts = function(){

    $http.get("/general_reports/mac=" + $scope.sensor + "/startDate=" + document.getElementById("id_start_date").value + "/range=" + $scope.range).then(function (response){

      $scope.tempReadouts = response.data;
      parseFloatReadouts();

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
         break;
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
                       slantedTextAngle: 45
                    }
    };

      // Instantiate and draw our chart, passing in some options.
      var chart = new google.visualization.LineChart(document.getElementById("chart_div"));
      chart.draw(data, options);

      $('#chart_div').show();
    });
  }
}
