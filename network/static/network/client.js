document.addEventListener("DOMContentLoaded", () => {

	// asynchronously create a post for the user
	document.querySelector("#create-post").onsubmit = function(){
		
		const content = document.querySelector("#content").value;
		
		// reset the textbox
		document.querySelector("#content").value = "";
		
		if (content.length >= 1)
		{
			const csrftoken = Cookies.get("csrftoken");
			const request = new Request("/create_post", {headers:{"X-CSRFToken": csrftoken}})

			const form = new FormData();
			form.append('content', content);

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
		return false;
	};
})