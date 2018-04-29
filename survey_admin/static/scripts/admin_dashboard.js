function addOptions() {
	var numOptions=document.getElementById("numOptions").value;
	console.log(numOptions);
	var i;
	var optNum;
	var optionHeader = document.getElementById('optionSelect');
	console.log(optionHeader);
	var rows = optionHeader.getElementsByTagName("input");
	while (rows.length)
		rows[0].parentNode.removeChild(rows[0]);

	for(i=0; i<numOptions;i++) {
		optNum=i+1;
		var input=document.createElement("input");
		input.setAttribute("type", "text");
		input.setAttribute("class", "form-control");
		input.setAttribute("id", "option");
		input.setAttribute("placeholder", "Option " + optNum);
		input.setAttribute("name","option["+i+"]");
		console.log("Appending Options");
		optionHeader.appendChild(input);
	}
}

function validateForm() {
	alert('validating form2');
	var inputs=document.forms["questionForm"].getElementsByTagName('input');
	var i, name;
	for (i=0; i<inputs.length; i++) {
		console.log(inputs[i].value);
		if (inputs[i].value.length == 0) {
			name=inputs[i].value;
			document.getElementsByName(name).setAttribute("id", "inputError");
		}
	}
}
