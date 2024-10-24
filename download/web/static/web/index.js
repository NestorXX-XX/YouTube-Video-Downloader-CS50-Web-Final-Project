
document.addEventListener("DOMContentLoaded", ()=>{

    document.querySelector('#w-icon-nav-menu').addEventListener('click', function() {
        const navMenu = document.querySelector('.w-nav[data-collapse="medium"] .w-nav-menu');
        const form = document.querySelector('.form');
        if (navMenu) {
            if (navMenu.style.display == 'block') {
                navMenu.style.animationName = "hide";
                navMenu.style.animationPlayState = 'running';
                form.style.animationPlayState = "running";
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

    document.querySelector("#download_video").addEventListener("submit", (event)=>{
        event.preventDefault(); 
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const progressContainer = document.getElementById("progress-container")
        const progressBar = document.getElementById('download-progress');
        const progressText = document.getElementById('progress-text');

        const format = document.querySelector("#select-format").value
        if (format=="mp3") {
            progressContainer.innerHTML = "Downloading...";
        }
        progressContainer.style.display = "block"
        progressBar.value = 0;
        progressText.innerText = '0%';

        fetch(`/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
              link: document.querySelector(`#link`).value,
              format: format
            })
          }) 
        .then(response => {
            if (response.ok) {
                document.querySelector("#error-download").style="display:none"
                const contentDisposition = response.headers.get('Content-Disposition');
                const filenameMatch = contentDisposition.match(/filename="(.+?)"/)
                filename = response.headers.get('X-Filename')
                const contentLength = response.headers.get('content-length');
                const total = parseInt(contentLength, 10);
                let loaded = 0;
                const reader = response.body.getReader();
                const stream = new ReadableStream({
                    start(controller) {
                        function push() {
                            reader.read().then(({ done, value }) => {
                                if (done) {
                                    controller.close();
                                    return;
                                }
                                loaded += value.byteLength;
                                progressBar.value = (loaded / total) * 100;
                                progressText.innerText = `${Math.round((loaded / total) * 100)}%`;
                                
                                controller.enqueue(value);
                                push();
                            }).catch(error => {
                                console.error('Download error:', error);
                                controller.error(error);
                            });
                        }
        
                        push();
                    }
                });
                
                return new Response(stream);
            } else {
                return response.json().then(error => {
                    throw new Error(error.error);
                });
            }
            })
        .then(response => response.blob())   
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();  
            window.URL.revokeObjectURL(url);
            progressContainer.innerHTML = "Download completed!";
            fetch('/history/new', {
                method: 'POST',
                body: JSON.stringify({
                  format: document.querySelector("#select-format").value,
                  link: document.querySelector(`#link`).value,
                  filename: filename
                })
              })

            fetch('/send_email', {
            method: 'POST',
            body: JSON.stringify({
                format: document.querySelector("#select-format").value,
                link: document.querySelector(`#link`).value,
                filename: filename
            })
            })
            progressContainer.style.animationPlayState = 'running';
            progressContainer.addEventListener('animationend', () => {
                progressContainer.remove()
                window.location.href = '';
                });
           
           
        })
        .catch(error => {
            progressContainer.style.display = "none"
            div= document.querySelector("#error-download")
            div.innerHTML = error
            div.style = "display:block"
            
            
        });


    });





});


function load_index() {

    document.getElementById("progress-container").style.display = "none"
    document.getElementById("error-download").style.display = "none"
    document.getElementById("link").value = ""
    document.getElementById("select-format").value = ""


}    

