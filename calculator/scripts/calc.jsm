// enable the buttons
$(function() {
  // load log click
  $('#load-calculator-log').click(function() {
    $('#calculator-log').load('/calculator/calc__loadlog/');
  });//click

  // delete log click
  $('#delete-calculator-log').click(function() {
    $('#calculator-log').load('/calculator/calc__deletelog/');
  });//click


  // note the embedded Python here
  console.log("Hello from calc.jsm: 2 + 2 = ${ 2 + 2 }");

});//func
