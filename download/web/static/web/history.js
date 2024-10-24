document.addEventListener("DOMContentLoaded", () => {

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


    fetch(`history_view_pages`)
    .then(response => response.json())
    .then(array => {
        array.pages.forEach(i => {
            let page = document.createElement("div");
            page.style = "display: none"
            page.id = `page${i.page}`
            document.querySelector("#pages").append(page);
            
         

            i.downloads.forEach(i => {
                let download = document.createElement("div");
                download.className = "download";
                download.innerHTML = `
                <div>
                  <h2 id="download${i.id}" style="font-size:3vh;"><a href="#" style="color:black">${i.filename}</a></h2>
                  <p id='link-${i.id}'><a href='${i.link}' target="_blank">${i.link}</a></p>
                  <p > ${i.timestamp}</p>
                  <button id="download-${i.id}"class="btn btn-primary ">Download</button>
                  <div id="progress-bar-container-${i.id}" style="margin-top:2vh;display:none" class="progress-bar2">
                    <progress id="download-progress-${i.id}" value="0" max="100" ></progress>
                    <span id="progress-text-${i.id}" style="font-family: Tahoma, Verdana, Segoe, sans-serif;">0%</span>
                    </div>
                </div>`;
        
                document.querySelector(`#${page.id}`).append(download);
                
                document.getElementById(`download-${i.id}`).addEventListener("click", ()=>{
                    download1(i.link,i.format,`progress-bar-container-${i.id}`,`download-progress-${i.id}`,`progress-text-${i.id}`)
                  });

              })

              bottons = document.createElement("div");
              bottons.innerHTML = `
                    ${ i.previous ? `<button id="previous${i.page}"class="btn btn-primary float-left" style="margin-top: 5vh; margin-bottom: 2vh;">Previous</button>`:""}
                    ${ i.next ? `<button id="next${i.page}"class="btn btn-primary float-right" style="margin-top: 5vh; margin-bottom: 2vh;">Next</button>`:""}
              `
              page.append(bottons)

              try {
              document.querySelector(`#previous${i.page}`).addEventListener( "click", () => {
                document.querySelector(`#page${i.page}`).style = "display:none"     
                document.querySelector(`#page${i.page-1}`).style = "display:block"

              });}
              catch{}

              try {
              document.querySelector(`#next${i.page}`).addEventListener( "click", () => {
                
                document.querySelector(`#page${i.page}`).style = "display:none"     
                document.querySelector(`#page${i.page+1}`).style = "display:block"
                
              });
              }
              catch{}
              
             
        });
        

    
    document.querySelector("#page1").style = "display: block"
        




      
    });








});




function download1(link,format,idcontainer,idbar,idtext) {

    fetch(`/download`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
          link: link,
          format: format
        })
      }) 
    .then(response => {
        if (response.ok) {
            progressContainer =  document.getElementById(idcontainer)
            progressBar = document.getElementById(idbar)
            progressText = document.getElementById(idtext) 
            progressContainer.style.display = "block"
            const contentDisposition = response.headers.get('Content-Disposition');
            const filenameMatch = contentDisposition.match(/filename="(.+?)"/);
            filename = filenameMatch[1];
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
        alert("Download completed!");
        
        progressContainer.style.animationPlayState = 'running';
            progressContainer.addEventListener('animationend', () => {
                progressContainer.remove()
                });
       
       
    })
    .catch(error => {
        alert(error)
        
        
    });





};