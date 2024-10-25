console.log("Probando la funcionalidad del js")

$(document).ready(function() {
    $('.select2').select2({
      placeholder: "select the permissions for this group",
      class:"bg-success",
    });
  
  });
  
  $(document).ready(function(){
    
    //Get the user string
    var userString = $("#string1").val();
    
    //Capitalize the first letter of the string
    userString = userString.substring(0,1).toUpperCase() + userString.substring(1);
  
    //Display the results
    $("#results").text(userString);
  
  });
