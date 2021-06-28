$(document).ready(function(){
	var arr = []
	var input = document.getElementById("key")
	var result_string = "";
	var word = "";
	var query;
	/*the autocomplete function takes two arguments,
  	the text field element and an array of possible autocompleted values:*/
  	var currentFocus;
	  /*execute a function when someone writes in the text field:*/
	  input.addEventListener("input", function(e) {
		query = $("#key").val();

		fetchData();


	  });
	  /*execute a function presses a key on the keyboard:*/
	  input.addEventListener("keydown", function(e) {
	      var x = document.getElementById(this.id + "autocomplete-list");
	      if (x) x = x.getElementsByTagName("div");
	      if (e.keyCode == 40) {
		/*If the arrow DOWN key is pressed,
		increase the currentFocus variable:*/
		currentFocus++;
		/*and and make the current item more visible:*/
		addActive(x);
	      } else if (e.keyCode == 38) { //up
		/*If the arrow UP key is pressed,
		decrease the currentFocus variable:*/
		currentFocus--;
		/*and and make the current item more visible:*/
		addActive(x);
	      } else if (e.keyCode == 13) {
		/*If the ENTER key is pressed, prevent the form from being submitted,*/
		e.preventDefault();
		if (currentFocus > -1) {
		  /*and simulate a click on the "active" item:*/
		  if (x) x[currentFocus].click();
		}
		closeAllLists(e);
		displayResult();
	      }
	  });
	  function addActive(x) {
	    /*a function to classify an item as "active":*/
	    if (!x) return false;
	    /*start by removing the "active" class on all items:*/
	    removeActive(x);
	    if (currentFocus >= x.length) currentFocus = 0;
	    if (currentFocus < 0) currentFocus = (x.length - 1);
	    /*add class "autocomplete-active":*/
	    x[currentFocus].classList.add("autocomplete-active");
	  }
	  function removeActive(x) {
	    /*a function to remove the "active" class from all autocomplete items:*/
	    for (var i = 0; i < x.length; i++) {
	      x[i].classList.remove("autocomplete-active");
	    }
	  }
	  function closeAllLists(elmnt) {
	    /*close all autocomplete lists in the document,
	    except the one passed as an argument:*/
	    var x = document.getElementsByClassName("autocomplete-items");
	    for (var i = 0; i < x.length; i++) {
	      if (elmnt != x[i] && elmnt != input) {
	      x[i].parentNode.removeChild(x[i]);
	    }
	  }
	}
	/*execute a function when someone clicks in the document:*/
	document.addEventListener("click", function (e) {
	    closeAllLists(e.target);
	});

	function displayResult(){



		console.log("value is : " + query);
                if(query.length > 0){

                var host = window.location.hostname;
                var port = window.location.port;

                var url = "http://"+ host + ":" + port + "/search/" + query;
                console.log(url);
                $.get(url, function(response){
                        var i,j,k;
                        console.log(response);
                        arr = []
                        for(i=0; i< response.results.length; i++){
                                result_string = "";
                                word = "";
                                result_string += "<ul>";
                                word = response.results[0].key;
                                arr.push(response.results[i].key);

                                for(j=0; j< response.results[0].data.length; j++){

                                        result_string += "<li><b>"+ response.results[0].data[j].pos +"</b>";
                                        result_string += "<ol>";
                                        for(k=0;k<response.results[0].data[j].content.length;k++){
                                                result_string += "<li>"+response.results[0].data[j].content[k].meaning;
                                                if(response.results[0].data[j].content[k].example != null && response.results[0].data[j].content[k].example != undefined){

                                                result_string += "</br><i>"+response.results[0].data[j].content[k].example+"</i>";
                                                }
                                                result_string += "</li>";
                                        }

                                        result_string += "</ol></li></br>";

				}
                                result_string += "</ul></br>";
				if(response.results[0].synonyms.length > 0){
					result_string += "<span>Synonyms: ";
					for(m = 0; m< response.results[0].synonyms.length; m++){
						if(m == response.results[0].synonyms.length - 1){
							result_string += "<b>"+response.results[0].synonyms[m] +"</b></span>";
						}else{
							result_string += "<b>"+response.results[0].synonyms[m] +"</b>, ";
						}
                               	}	 }
                        }

			if(word != query){
				document.getElementById("word").innerHTML = "";
				document.getElementById("result_list").innerHTML = "";
				result_string = "<div style='text-align: center'><p><b style='font-size: 40px'>"+query+"</b> <span style='font-size: 30px'> not found</span></p></div>";
				$("#result_list").append(result_string);

			}else{
				document.getElementById("word").innerHTML = "";
	                        $("#word").append(word);

        	                document.getElementById("result_list").innerHTML = "";
                	        $("#result_list").append(result_string);

			}
		});
	   }
	};


	function fetchData(){


                console.log("value is : " + query);
                if(query.length > 0){

			var host = window.location.hostname;
			var port = window.location.port;

			var url = "http://"+ host + ":" + port + "/api?key=" + query;
			console.log(url);
			$.get(url, function(response){
				var i,j,k;
				console.log(response);
				arr = []
				for(i=0; i< response.results.length; i++){
					result_string = "";
					word = "";
					result_string += "<ul>";
					word = response.results[0].key;
					arr.push(response.results[i].key);
				}
			      var a, b, i, val = input.value;
			      /*close any already open lists of autocompleted values*/
			      closeAllLists();
			      if (!val) { return false;}
			      currentFocus = -1;
			      /*create a DIV element that will contain the items (values):*/
			      a = document.createElement("DIV");
			      a.setAttribute("id", input.id + "autocomplete-list");
			      a.setAttribute("class", "autocomplete-items");
			      /*append the DIV element as a child of the autocomplete container:*/
			      input.parentNode.appendChild(a);
			      /*for each item in the array...*/
			      for (i = 0; i < arr.length; i++) {
				/*check if the item starts with the same letters as the text field value:*/
				if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
				  /*create a DIV element for each matching element:*/
				  b = document.createElement("DIV");
				  /*make the matching letters bold:*/
				  b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
				  b.innerHTML += arr[i].substr(val.length);
				  /*insert a input field that will hold the current array item's value:*/
				  b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
				  /*execute a function when someone clicks on the item value (DIV element):*/
				      b.addEventListener("click", function(e) {
				      /*insert the value for the autocomplete text field:*/
				      input.value = this.getElementsByTagName("input")[0].value;
				      /*close the list of autocompleted values,
				      (or any other open lists of autocompleted values:*/
				      closeAllLists();
					query = input.value;
				      displayResult();
				  });
				 a.appendChild(b);
				}
			     }
			});
		}


	}


});
