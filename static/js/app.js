$(document).foundation()

var app = angular.module('TempView', []);
app.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
}).run();
