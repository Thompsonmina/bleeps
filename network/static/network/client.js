document.addEventListener("DOMContentLoaded", () => {

	// asynchronously create a post for the user
	document.querySelector("#create-post").onsubmit = function(){
		const content = document.querySelector("#content").value;
		
		// reset the textbox
		document.querySelector("#content").value = "";
		if (content.length >= 1)
		{
			sendFormDataOnPost("/create_post", {content: content})	
		}
		return false;
	};

	document.querySelectorAll(".edit_post").forEach(btn =>{
		btn.onclick = () => {
			const currentp = btn.parentElement.children[1]
			const formertext = currentp.innerText;
			textbox = document.querySelector("#edit-textbox")

			$("#edit-post-modal").modal("show");
			textbox.value = formertext;


			document.querySelector("#edit-post").onsubmit = function(){
			
				content = textbox.value
				if (content.length >= 1)
				{
					sendFormDataOnPost("/edit_post/" + `${btn.dataset.id}`, {content: content})	
				}
				currentp.innerText = content
				$("#edit-post-modal").modal("hide");
				return false;
				
			};
			console.log("pheew");

		}
	});
})



function sendFormDataOnPost(route, data)
{
	const csrftoken = Cookies.get("csrftoken");
	const request = new Request(route, {headers:{"X-CSRFToken": csrftoken}})

	const form = new FormData();
	for (const input in data){
		form.append(`${input}`, data[input])
	}

	fetch(request,{
		method: "POST",
		body: form,
		mode: "same-origin"
	})
    .then(response => response.json())
    .then(data => {    
        if (data.success)
        {
        	console.log("success")
        }
        else{ console.log(data.error) }
    });
}