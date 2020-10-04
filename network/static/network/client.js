document.addEventListener("DOMContentLoaded", () => {

	// asynchronously create a post for the user
	if (document.querySelector("#create-post")){
		document.querySelector("#create-post").onsubmit = function(){
		const content = document.querySelector("#content").value;
		
		// reset the textbox
		document.querySelector("#content").value = "";
		if (content.length >= 1)
		{
			sendFormDataOnPost("/create_post", {content: content})
			.then(data => {
				if (!data.success){
					alert("post not sent, something went wrong")
				}
				else{
				 		console.log(data.error)
				 	}
			})
		}
		return false;
		};
	}
	

	document.querySelectorAll(".edit_post").forEach(btn =>{
		btn.onclick = () => {
			const currentp = btn.parentElement.querySelector(".profile-text");
			const formertext = currentp.innerText;
			textbox = document.querySelector("#edit-post-modal-textbox");

			$("#edit-post-modal").modal("show");
			textbox.value = formertext;

			document.querySelector("#edit-post-modal-form").onsubmit = function() {
				content = textbox.value
				if (content.length >= 1)
				{
					sendFormDataOnPost("/edit_post/" + `${btn.dataset.id}`, {content: content})	
					.then(data => {
						if (data.success){
							currentp.innerText = content
							$("#edit-post-modal").modal("hide");
						}
						else{
				 		console.log(data.error)
				 	}
					})
				}
				return false;
			};
			console.log("pheew");

		}
	});

	document.querySelectorAll(".likebtn").forEach(btn =>{

		btn.onclick = () => {
			let likecount = btn.parentElement.querySelector(".likes-count")
			if (btn.dataset.action === "liked"){
				btn.dataset.action = "unliked";
				sendFormDataOnPost("/unlike", {post_id: btn.dataset.id})
				.then(data => {
					if(data.success) {
						btn.classList.remove("fas")
						btn.classList.add("far")
						likecount.innerText = parseInt(likecount.innerText) - 1
					}
				});
			}
			else{
				btn.dataset.action = "liked";
				sendFormDataOnPost("/like", {post_id: btn.dataset.id})
				.then(data => {
					if (data.success){
						btn.classList.remove("far")
						btn.classList.add("fas")
						likecount.innerText = parseInt(likecount.innerText) + 1
					}
				});
				
			}
		};
	});

// work in progress
	const editProfileButton = document.querySelector(".edit_profile")
	if (editProfileButton){
		editProfileButton.onclick = () => {
			const currentbio = editProfileButton.parentElement.querySelector(".current-bio")
			const formertext = currentbio.innerText;
			textbox = document.querySelector("#edit-profile-modal-textbox")

			$("#edit-profile-modal").modal("show");
			textbox.value = formertext;

			document.querySelector("#edit-profile-modal-form").onsubmit = function(){
				content = textbox.value
				if (content.length >= 1){
					sendFormDataOnPost("/edit_profile/" + `${editProfileButton.dataset.name}`, {bio: content})	
					.then(data => {
						if (data.success){
							currentbio.innerText = content
							$("#edit-profile-modal").modal("hide");
						}
						else{
				 		console.log(data.error)
				 		}
					});
				}
				return false;
				
			};

		};
	}
	
	
	document.querySelectorAll(".follow-status").forEach(btn =>{
		
		btn.onclick = () => {
			if (btn.dataset.action === "follow"){
			
				sendFormDataOnPost("/follow", {otheruser_id: btn.dataset.id})
				.then(data => {
					if (data.success)
				 	{
				 		btn.innerText = "Unfollow"
				 		btn.dataset.action = "unfollow"
				 	}
				 	else{
				 		console.log(data.error)
				 	}
				 })
			}
			else{
				sendFormDataOnPost("/unfollow", {otheruser_id: btn.dataset.id})
				.then(data => {
					if (data.success)
				 	{
				 		btn.innerText = "Follow"
				 		btn.dataset.action = "follow"
				 	}
				 	else{
				 		console.log(data.error)
				 	}
				 })
			}
		}
	});

});

async function sendFormDataOnPost(route, data)
{
	const csrftoken = Cookies.get("csrftoken");
	const request = new Request(route, {headers:{"X-CSRFToken": csrftoken}});

	const form = new FormData();
	for (const input in data){
		form.append(`${input}`, data[input])
	}

	response = await fetch(request,{
		method: "POST",
		body: form,
		mode: "same-origin"
	})
    return await response.json();
   
}