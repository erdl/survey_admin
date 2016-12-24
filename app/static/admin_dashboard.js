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
