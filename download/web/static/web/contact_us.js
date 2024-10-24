document.addEventListener("DOMContentLoaded", () => {

    document.getElementById("message").value = ""
    document.getElementById("subject").value = ""

    document.querySelector('#w-icon-nav-menu').addEventListener('click', function() {
        const navMenu = document.querySelector('.w-nav[data-collapse="medium"] .w-nav-menu');
        if (navMenu) {
            if (navMenu.style.display == 'block') {
                navMenu.style.animationName = "hide";
                navMenu.style.animationPlayState = 'running';
                navMenu.addEventListener('animationend', () => {
                    navMenu.style.display = 'none';
                });

            }
            else {
                navMenu.style.animationName = "show";
                navMenu.style.display = 'block';
                navMenu.style.animationPlayState = 'running';
                navMenu.addEventListener('animationend', () => {
                    navMenu.style.display = 'block';
                });

            }
        }
    });

    document.getElementById("contact_form").addEventListener("submit", async (event) => {
        event.preventDefault(); // Prevents the default form submission
    
        const form = event.target; // Get the form element
        const formData = new FormData(form); // Create a FormData object from the form
    
        try {
            const response = await fetch(form.action, {
                method: form.method, // Use the method specified in the form
                body: formData, // Send form data as the request body
            });
    
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
    
            const result = await response.json(); // Parse the JSON response
    
            // Display success message
            document.getElementById("message_div").style.display = "block";
            document.getElementById("message-text").innerHTML = 'Your message was sent successfully!';
            document.getElementById("message_div").style.backgroundColor = "#d4edda";
            document.getElementById("message_div").style.border = "#d4edda";

        } catch (error) {
            console.error('Error:', error);
            // Display error message
            document.getElementById("message_div").style.display = "block";
            document.getElementById("message-text").innerHTML = 'There was an error sending your message. Please try again.';
            document.getElementById("message_div").style.backgroundColor = "#f8d7da";
            document.getElementById("message_div").style.border = "#f8d7da";
        }
    });
    
   
    


});

function hideMessage() {
    const messageBox = document.getElementById('message_div');
    messageBox.style.display = 'none'; // Hide the message box
}
