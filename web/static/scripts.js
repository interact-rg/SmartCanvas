document.addEventListener("DOMContentLoaded", async function (event) {
    const clientFeed = document.getElementById("clientFeed");
    const serverFeed = document.getElementById("serverFeed");
    const canvas = document.getElementById("canvas");
    const itemsResized = false;

    const socket = io.connect({ reconnection: false });

    socket.on("connect", () => {
      console.log("Connected");
    });

    socket.on("disconnect", () => {
      console.log("Disconnected");
    });

    socket.on("connect_error", (error) => {
      console.log("Connect error! " + error);
    });

    socket.on("connect_timeout", (error) => {
      console.log("Connect timeout! " + error);
    });

    socket.on("error", (error) => {
      console.log("Error! " + error);
    });

    socket.on("consume", (msg) => {
      var img = new Image;

      const serveFeedCtx = serverFeed.getContext("2d");
      img.onload = function(){
        serveFeedCtx.drawImage(img, 0, 0, canvas.width, canvas.height);
      };

      img.src = msg;
    });

    page_identifier = document.getElementById("page_identifier");
    //Normal mode:
    if (page_identifier.textContent == "normal") {
        console.log("Do normal site stuffs")
        //TODO: use 'diplay: none' instead of 'visibility: hidden' to make invisible items not take space (or preferably make this more like fullscreen mode)
        socket.on("update_ui_response", (msg) => {
            console.log(msg)
            var visibles = []
            //visible messages visible
            for (var key in msg){
              var html_item = document.getElementById(key);
              if (key != "hold_timer" && key != "countdown") {
                html_item.style.visibility = 'visible'
                html_item.textContent = msg[key];
                visibles.push(key);
              }
              else if (key == "hold_timer") {
                html_item = document.getElementById("hold_progress");
                html_item.value = msg[key] * 100;
                if (msg[key] <= 0 || msg[key] >= 1) {
                  html_item.style.visibility = 'hidden';
                }
                else {
                  html_item.style.visibility = 'visible';
                }
              }
              else if (key == "countdown") {
                if (msg[key] == "0") {
                  html_item = document.getElementById("countdown");
                  html_item.style.visibility = "hidden";
                }
                else {
                  html_item = document.getElementById("countdown");
                  html_item.style.visibility = "visible";
                  html_item = document.getElementById("countdown_value");
                  html_item.textContent = msg[key]
                }
              }
            }
            console.log(visibles)
            //hidden messages invisible
            var childas = document.getElementById('ui').getElementsByTagName('a');
            for( var i=0; i< childas.length; i++ ) {
              var childa = childas[i];
              if (!visibles.includes(childa.id)) {
                  if (childa.id != "hold_timer") {
                      html_item = document.getElementById(childa.id);
                      console.log("setting inviisble", html_item.id)
                      try {
                          //html_item.textContent = null;
                          html_item.style.visibility = "hidden";
                      } catch (error) {
                          console.log("error with", childa.id, error)
                      }
                }
              }
            }
        });
    }
    //Fullscreen mode
    else if (page_identifier.textContent == "fullscreen") {
        console.log("DO fs stuffs")
        socket.on("update_ui_response", (msg) => {
            console.log(msg);
            var msgs = [];
            for (var key in msg){
                if (key != "hold_timer" && key != "countdown" && key !="idle_text_1") {
                  msgs.push(msg[key]);
                }
                else if (key == "hold_timer") {
                  var html_item = document.getElementById("hold_progress");
                  html_item.value = msg[key] * 100;
                  if (msg[key] <= 0 || msg[key] >= 1) {
                    html_item.style.visibility = 'hidden';
                  }
                  else {
                    html_item.style.visibility = 'visible';
                  }
                }
                else if (key == "countdown") {
                  if (msg[key] == "0") {
                    var html_item = document.getElementById("countdown");
                    html_item.style.visibility = "hidden";
                  }
                  else {
                    var html_item = document.getElementById("countdown");
                    html_item.style.visibility = "visible";
                    html_item = document.getElementById("countdown_value");
                    html_item.textContent = msg[key]
                  }
                }
            }
            var children = document.getElementById("fs_ui").children;
            for (var i = 0; i < children.length; i++) {
              if (i <= msgs.length - 1) {
                children[i].textContent = msgs[i];
                children[i].style.display = 'block';
              }
              else {
                children[i].style.display = 'none';
              }
            }
        });
    }
    //Fullscreen with symbols instead of text (experimental)
    else if (page_identifier.textContent == "fullscreen_symbol") {
        socket.on("update_ui_response", (msg) => {
            console.log(msg);
            var used_keys = [];
            for (var key in msg){
                if (key != "hold_timer" && key != "countdown" && key !="idle_text_1") {
                  used_keys.push(key)
                  ui_element_div = document.getElementById(key);
                  ui_element_div.style.display = "block";
                  if (key == "filter_name") {
                    ui_element_div.children[0].textContent = msg[key];
                  }
                }
                else if (key == "hold_timer") {
                  var html_item = document.getElementById("hold_progress");
                  html_item.value = msg[key] * 100;
                  if (msg[key] <= 0 || msg[key] >= 1) {
                    html_item.style.visibility = 'hidden';
                  }
                  else {
                    html_item.style.visibility = 'visible';
                  }
                }
                else if (key == "countdown") {
                  if (msg[key] == "0") {
                    var html_item = document.getElementById("countdown");
                    html_item.style.visibility = "hidden";
                  }
                  else {
                    var html_item = document.getElementById("countdown");
                    html_item.style.visibility = "visible";
                    html_item = document.getElementById("countdown_value");
                    html_item.textContent = msg[key]
                  }
                }
            }
            var children = document.getElementById("fs_ui").children;
            var to_hide_element = null;
            for (var i = 0; i < children.length; i++) {
              if (children[i].tagName == "DIV" && !(used_keys.includes(children[i].id))) {
                to_hide_element = document.getElementById(children[i].id);
                to_hide_element.style.display = "none";
              }
            }
        });
    }
    

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      let stream = await navigator.mediaDevices.getUserMedia({
        video: {
            width: { ideal: 1280 },
            height: { ideal: 720 } 
        },
        audio: false,
      });
      clientFeed.srcObject = stream;

      canvas
        .getContext("2d")
        .drawImage(clientFeed, 0, 0, canvas.width, canvas.height);
      
      const FPS = 20;
      let interval = setInterval(() => {
        canvas
          .getContext("2d")
          .drawImage(clientFeed, 0, 0, canvas.width, canvas.height);
        const image_data_url = canvas.toDataURL("image/jpeg");
        socket.emit("produce", image_data_url)
      }, 1000/FPS);
    }

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      let interval = setInterval(() => {
        socket.emit("update_ui_request")
      }, 200);
    }

    //Once camera is initialized, adjust offsets of UI items based on resolution (TODO: on fullscreen resize to fit window)
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia && !itemsResized) {
        const canvass = document.getElementById("canvas");
        const hold = document.getElementById("hold_progress");
        const ctr = document.getElementById("countdown_value");
        if (canvass.width == 640 && canvas.height == 480) {
            console.log("setting UI to 480p")
            hold.style['transform'] = 'translate(140%,2800%)';
            ctr.style['transform'] = 'transform: translate(350%, 100%)';
        }
        else if (canvass.width == 1280 && canvas.height == 720) {
            console.log("setting UI to 720p")
            hold.style['transform'] = 'translate(350%,4000%)';
            ctr.style['transform'] = 'translate(820%, 150%)';
        }
    }
    
});